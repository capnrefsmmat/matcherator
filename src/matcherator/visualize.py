"""Visualization and auditing tool for matcherator pattern-matching rules."""

import argparse
import html
import importlib.resources
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from jinja2 import Environment, PackageLoader, select_autoescape
from spacy.tokens import Doc


def _load_builtin_rules() -> Dict[str, Dict[str, Any]]:
    """Load all rules from built-in rulesets in matcherator.rules."""
    all_rules: Dict[str, Dict[str, Any]] = {}

    rules_dir = importlib.resources.files("matcherator.rules")
    for item in rules_dir.iterdir():
        if item.name.endswith(".json"):
            try:
                rule_text = item.read_text()
                rules_json = json.loads(rule_text)
                ruleset_name = item.name

                for matcher_type in ("Matcher", "DependencyMatcher", "PhraseMatcher", "Derived"):
                    for rule_name, rule_def in rules_json.get(matcher_type, {}).items():
                        # Preserve existing if already loaded, but record metadata
                        if rule_name not in all_rules:
                            all_rules[rule_name] = {
                                "name": rule_name,
                                "matcher_type": matcher_type,
                                "ruleset": ruleset_name,
                                "description": rule_def.get("description", ""),
                                "comment": rule_def.get("comment", ""),
                                "examples": rule_def.get("examples", []),
                                "counterexamples": rule_def.get("counterexamples", []),
                                "rules": rule_def.get("rules", []),
                                "derived": rule_def.get("derived", matcher_type == "Derived"),
                            }
            except Exception:
                continue

    return all_rules


def _resolve_rules(
    rules_input: Optional[Union[Dict[str, Any], str, Sequence[Union[Dict[str, Any], str]]]] = None
) -> Dict[str, Dict[str, Any]]:
    """Resolve and merge rules from built-ins and optional user input."""
    merged = _load_builtin_rules()

    if rules_input is None:
        return merged

    inputs = [rules_input] if isinstance(rules_input, (dict, str)) else rules_input

    for r in inputs:
        if isinstance(r, str):
            if r.endswith(".json") and not Path(r).exists():
                try:
                    rule_text = importlib.resources.files("matcherator.rules").joinpath(r).read_text()
                    r_dict = json.loads(rule_text)
                    ruleset_name = r
                except Exception:
                    r_dict = json.loads(Path(r).read_text())
                    ruleset_name = Path(r).name
            else:
                r_dict = json.loads(Path(r).read_text())
                ruleset_name = Path(r).name
        elif isinstance(r, dict):
            r_dict = r
            ruleset_name = "custom"
        else:
            continue

        for matcher_type in ("Matcher", "DependencyMatcher", "PhraseMatcher", "Derived"):
            for rule_name, rule_def in r_dict.get(matcher_type, {}).items():
                merged[rule_name] = {
                    "name": rule_name,
                    "matcher_type": matcher_type,
                    "ruleset": ruleset_name,
                    "description": rule_def.get("description", ""),
                    "comment": rule_def.get("comment", ""),
                    "examples": rule_def.get("examples", []),
                    "counterexamples": rule_def.get("counterexamples", []),
                    "rules": rule_def.get("rules", []),
                    "derived": rule_def.get("derived", matcher_type == "Derived"),
                }

    return merged


def _generate_palette(num_colors: int) -> List[Dict[str, str]]:
    """Generate visually distinct, aesthetically pleasing HSL colors."""
    palette = []
    # Curated golden-angle hue distribution
    golden_ratio_conjugate = 0.618033988749895
    h = 0.1

    for i in range(num_colors):
        h = (h + golden_ratio_conjugate) % 1.0
        hue = int(h * 360)
        palette.append({
            "bg": f"hsla({hue}, 85%, 88%, 0.85)",
            "bg_subtle": f"hsla({hue}, 85%, 94%, 0.5)",
            "border": f"hsl({hue}, 70%, 45%)",
            "text": f"hsl({hue}, 90%, 25%)",
            "badge_bg": f"hsl({hue}, 75%, 45%)",
            "badge_text": "#ffffff",
        })
    return palette


def extract_doc_data(
    doc: Doc,
    rules: Optional[Union[Dict[str, Any], str, Sequence[Union[Dict[str, Any], str]]]] = None,
    include_derived: bool = False,
) -> Dict[str, Any]:
    """Extract tokens, sentences, matches, and metadata from a spaCy Doc for visualization.

    :param doc: Processed spaCy Doc with matcherator extension attributes.
    :param rules: Optional rules dictionary, JSON filename, or list of rulesets.
    :param include_derived: If True, include intermediate/derived rules that are
      normally filtered out.
    :return: Dictionary containing tokens, sentences, features, and document statistics.
    """
    rule_metadata = _resolve_rules(rules)

    # 1. Discover all matcherator extensions on doc
    pipe_extensions = []
    # Check registered Doc extensions
    if hasattr(Doc, "_extensions"):
        for ext in Doc._extensions.keys():
            if ext.startswith("matcherator_") and not ext.endswith(("_features", "_stats")):
                if hasattr(doc._, ext) and getattr(doc._, ext) is not None:
                    pipe_extensions.append(ext)

    # Fallback to known default pipes if not discovered via _extensions
    for fallback_pipe in ("matcherator_biber", "matcherator_generic"):
        if fallback_pipe not in pipe_extensions and Doc.has_extension(fallback_pipe):
            val = getattr(doc._, fallback_pipe, None)
            if val is not None:
                pipe_extensions.append(fallback_pipe)

    # 2. Extract matches from all active pipes
    raw_feature_matches: Dict[str, List[Any]] = defaultdict(list)
    valid_features: set = set()
    computed_stats: Dict[str, Any] = {}

    for pipe in pipe_extensions:
        matches_dict = getattr(doc._, pipe, {})
        if isinstance(matches_dict, dict):
            for k, v in matches_dict.items():
                if v:
                    raw_feature_matches[k].extend(v)

        features_list = getattr(doc._, pipe + "_features", None)
        if features_list:
            valid_features.update(features_list)

        stats_dict = getattr(doc._, pipe + "_stats", None)
        if stats_dict and isinstance(stats_dict, dict):
            computed_stats.update(stats_dict)

    # If no valid_features set explicitly, consider all non-derived matched rules as valid
    if not valid_features:
        valid_features = {
            k for k in raw_feature_matches.keys()
            if not rule_metadata.get(k, {}).get("derived", False)
        }

    # 3. Process matches into normalized structures
    features_data: Dict[str, Dict[str, Any]] = {}
    token_to_match_ids: Dict[int, List[str]] = defaultdict(list)
    match_counter = 0

    all_matched_feature_names = sorted(raw_feature_matches.keys())
    # Filter derived features if include_derived is False
    filtered_feature_names = [
        f for f in all_matched_feature_names
        if include_derived or f in valid_features or not rule_metadata.get(f, {}).get("derived", False)
    ]

    colors = _generate_palette(len(filtered_feature_names))

    for feat_idx, feature_name in enumerate(filtered_feature_names):
        matches_list = raw_feature_matches[feature_name]
        feat_meta = rule_metadata.get(feature_name, {})
        matcher_type = feat_meta.get("matcher_type", "Matcher")

        color_scheme = colors[feat_idx] if feat_idx < len(colors) else {
            "bg": "hsla(200, 85%, 88%, 0.85)",
            "bg_subtle": "hsla(200, 85%, 94%, 0.5)",
            "border": "hsl(200, 70%, 45%)",
            "text": "hsl(200, 90%, 25%)",
            "badge_bg": "hsl(200, 75%, 45%)",
            "badge_text": "#ffffff",
        }

        processed_matches = []
        for raw_match in matches_list:
            # Determine token indices
            if matcher_type in ("Matcher", "PhraseMatcher") and isinstance(raw_match, (list, tuple)) and len(raw_match) == 2 and raw_match[0] < raw_match[1]:
                token_indices = list(range(raw_match[0], raw_match[1]))
            elif matcher_type == "DependencyMatcher" and isinstance(raw_match, (list, tuple)):
                token_indices = sorted(list(raw_match))
            elif isinstance(raw_match, tuple) and len(raw_match) == 2 and raw_match[0] < raw_match[1]:
                # 2-tuple (start, end) representing a half-open token slice [start, end)
                token_indices = list(range(raw_match[0], raw_match[1]))
            elif isinstance(raw_match, (list, tuple)):
                token_indices = sorted(list(raw_match))
            elif isinstance(raw_match, int):
                token_indices = [raw_match]
            else:
                continue

            if not token_indices:
                continue

            match_id = f"m_{match_counter}"
            match_counter += 1

            min_idx = min(token_indices)
            max_idx = max(token_indices)
            is_contiguous = (token_indices == list(range(min_idx, max_idx + 1)))

            if is_contiguous:
                matched_text = doc[min_idx:max_idx + 1].text
            else:
                matched_text = " ... ".join(doc[i].text for i in token_indices)

            # Find sentence index
            sent_idx = 0
            for s_i, sent in enumerate(doc.sents):
                if sent.start <= min_idx < sent.end:
                    sent_idx = s_i
                    break

            match_obj = {
                "id": match_id,
                "feature_name": feature_name,
                "token_indices": token_indices,
                "span_start": min_idx,
                "span_end": max_idx + 1,
                "is_contiguous": is_contiguous,
                "matched_text": matched_text,
                "sent_index": sent_idx,
                "color": color_scheme,
            }
            processed_matches.append(match_obj)

            for tok_idx in token_indices:
                if 0 <= tok_idx < len(doc):
                    token_to_match_ids[tok_idx].append(match_id)

        features_data[feature_name] = {
            "name": feature_name,
            "description": feat_meta.get("description", ""),
            "comment": feat_meta.get("comment", ""),
            "examples": feat_meta.get("examples", []),
            "counterexamples": feat_meta.get("counterexamples", []),
            "rules": feat_meta.get("rules", []),
            "matcher_type": matcher_type,
            "ruleset": feat_meta.get("ruleset", ""),
            "is_derived": feat_meta.get("derived", False),
            "color": color_scheme,
            "match_count": len(processed_matches),
            "matches": processed_matches,
        }

    # 4. Extract token linguistics and metadata
    tokens_data = []
    for token in doc:
        tok_matches = token_to_match_ids.get(token.i, [])
        tokens_data.append({
            "id": token.i,
            "text": token.text,
            "whitespace": token.whitespace_,
            "idx": token.idx,
            "end_idx": token.idx + len(token.text),
            "lemma": token.lemma_,
            "pos": token.pos_,
            "tag": token.tag_,
            "dep": token.dep_,
            "head": token.head.i,
            "head_text": token.head.text,
            "morph": str(token.morph) if token.morph else "",
            "is_sent_start": bool(token.is_sent_start),
            "is_punct": token.is_punct,
            "is_space": token.is_space,
            "matches": tok_matches,
        })

    # 5. Extract sentences
    sentences_data = []
    for i, sent in enumerate(doc.sents):
        sentences_data.append({
            "id": i,
            "start": sent.start,
            "end": sent.end,
            "text": sent.text,
        })

    # 6. Unmatched rules in ruleset (for auditing completeness)
    unmatched_rules = []
    for rule_name, rule_def in sorted(rule_metadata.items()):
        if rule_name not in features_data and not rule_def.get("derived", False):
            unmatched_rules.append({
                "name": rule_name,
                "description": rule_def.get("description", ""),
                "matcher_type": rule_def.get("matcher_type", ""),
                "ruleset": rule_def.get("ruleset", ""),
                "examples": rule_def.get("examples", []),
                "counterexamples": rule_def.get("counterexamples", []),
            })

    # 7. Document statistics
    word_tokens = [t for t in doc if not t.is_punct and not t.is_space]
    stats = {
        "total_tokens": len(doc),
        "word_tokens": len(word_tokens),
        "sentence_count": len(sentences_data),
        "total_matches": sum(f["match_count"] for f in features_data.values()),
        "distinct_features": len(features_data),
        "unmatched_rules_count": len(unmatched_rules),
        "computed_stats": computed_stats,
    }

    return {
        "text": doc.text,
        "tokens": tokens_data,
        "sentences": sentences_data,
        "features": features_data,
        "unmatched_rules": unmatched_rules,
        "stats": stats,
    }


def render(
    doc: Doc,
    rules: Optional[Union[Dict[str, Any], str, Sequence[Union[Dict[str, Any], str]]]] = None,
    title: Optional[str] = None,
    include_derived: bool = False,
    **kwargs: Any,
) -> str:
    """Render a spaCy Doc with matcherator annotations as a standalone interactive HTML string.

    :param doc: Processed spaCy Doc with matcherator extension attributes.
    :param rules: Optional rules dictionary, JSON filename, or list of rulesets.
    :param title: Custom page title.
    :param include_derived: If True, include intermediate/derived rules.
    :return: HTML string.
    """
    data = extract_doc_data(doc, rules=rules, include_derived=include_derived)

    env = Environment(
        loader=PackageLoader("matcherator"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("audit.html")

    page_title = title or "Matcherator Rule Audit"

    return template.render(
        title=page_title,
        doc_data=data,
        doc_json=json.dumps(data),
        **kwargs,
    )


def visualize(
    doc: Doc,
    output_path: Optional[Union[str, Path]] = None,
    rules: Optional[Union[Dict[str, Any], str, Sequence[Union[Dict[str, Any], str]]]] = None,
    title: Optional[str] = None,
    include_derived: bool = False,
    **kwargs: Any,
) -> str:
    """Visualize pattern matches on a spaCy Doc.

    If `output_path` is specified, writes the HTML to disk. Returns the HTML string.

    :param doc: Processed spaCy Doc with matcherator extension attributes.
    :param output_path: Optional file path to save the HTML page.
    :param rules: Optional rules dictionary, JSON filename, or list of rulesets.
    :param title: Custom page title.
    :param include_derived: If True, include intermediate/derived rules.
    :return: HTML string.
    """
    html_content = render(
        doc,
        rules=rules,
        title=title,
        include_derived=include_derived,
        **kwargs,
    )

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_content, encoding="utf-8")

    return html_content


def audit(
    doc: Doc,
    output_path: Optional[Union[str, Path]] = None,
    rules: Optional[Union[Dict[str, Any], str, Sequence[Union[Dict[str, Any], str]]]] = None,
    title: Optional[str] = None,
    include_derived: bool = False,
    **kwargs: Any,
) -> str:
    """Audit pattern matches on a spaCy Doc (alias for `visualize`).

    :param doc: Processed spaCy Doc with matcherator extension attributes.
    :param output_path: Optional file path to save the HTML page.
    :param rules: Optional rules dictionary, JSON filename, or list of rulesets.
    :param title: Custom page title.
    :param include_derived: If True, include intermediate/derived rules.
    :return: HTML string.
    """
    return visualize(
        doc,
        output_path=output_path,
        rules=rules,
        title=title,
        include_derived=include_derived,
        **kwargs,
    )


def main() -> None:
    """CLI entrypoint for auditing text patterns."""
    import spacy

    parser = argparse.ArgumentParser(description="Audit pattern-matching rules on a sample text.")
    parser.add_argument("text", nargs="+", help="Sample text to audit")
    parser.add_argument("--model", default="en_core_web_sm", help="spaCy model name (default: en_core_web_sm)")
    parser.add_argument("--ruleset", default="pseudobiber.json", help="Ruleset JSON filename or pipe (default: pseudobiber.json)")
    parser.add_argument("-o", "--output", default="audit.html", help="Output HTML file path (default: audit.html)")
    parser.add_argument("--title", default="Matcherator Rule Audit", help="Page title")
    parser.add_argument("--derived", action="store_true", help="Include derived/intermediate rules")

    args = parser.parse_args()
    text = " ".join(args.text)

    nlp = spacy.load(args.model, disable=["ner"])

    # Load appropriate pipe
    if args.ruleset == "pseudobiber.json":
        import matcherator.biber  # noqa: F401
        nlp.add_pipe("matcherator_biber")
    else:
        import matcherator.generic  # noqa: F401
        nlp.add_pipe("matcherator_generic", config={"rules": args.ruleset})

    doc = nlp(text)
    visualize(doc, output_path=args.output, title=args.title, include_derived=args.derived)
    print(f"Audit report generated: {args.output}")


if __name__ == "__main__":
    main()

"""Audit pattern-matching rules on a sample text and produce an interactive HTML report."""

import argparse
import spacy

import matcherator
import matcherator.biber
import matcherator.generic


def main():
    parser = argparse.ArgumentParser(
        description="Audit pattern-matching rules on a sample text and produce an interactive HTML report."
    )
    parser.add_argument("text", nargs="+", help="Sample text to audit")
    parser.add_argument(
        "--model",
        default="en_core_web_sm",
        help="spaCy model to use (default: en_core_web_sm)",
    )
    parser.add_argument(
        "--ruleset",
        default="pseudobiber.json",
        help="Ruleset JSON filename or 'pseudobiber.json' (default: pseudobiber.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="audit.html",
        help="Output HTML file path (default: audit.html)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Custom title for the audit page",
    )
    parser.add_argument(
        "--derived",
        action="store_true",
        help="Include derived/intermediate rules in the output",
    )

    args = parser.parse_args()
    text = " ".join(args.text)

    nlp = spacy.load(args.model, disable=["ner"])

    if args.ruleset == "pseudobiber.json":
        nlp.add_pipe("matcherator_biber")
    else:
        nlp.add_pipe("matcherator_generic", config={"rules": args.ruleset})

    doc = nlp(text)

    page_title = args.title or f"Matcherator Audit: {args.ruleset}"
    matcherator.visualize(
        doc,
        output_path=args.output,
        rules=args.ruleset,
        title=page_title,
        include_derived=args.derived,
    )
    print(f"Rule audit report written to: {args.output}")


if __name__ == "__main__":
    main()

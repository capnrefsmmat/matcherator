"""Match a text against rules."""

import argparse
import json
from collections import defaultdict, namedtuple

import spacy
from spacy.matcher import Matcher, DependencyMatcher, PhraseMatcher
from spacymoji import Emoji

import pandas as pd

Matchers = namedtuple("Matchers",
                      ["nlp", "plain", "dependency", "phrase", "feature_names"])

def initialize_matchers(rules, model):
    """Initialize matchers from a rule specification.

    The rule spec is read from the JSON rule file. We then initialize spaCy
    matchers and load the rules. Returns the three matchers (Matcher,
    DependencyMatcher, and PhraseMatcher) in a namedtuple.
    """

    # no need for named-entity recognition
    nlp = spacy.load(model, disable=["ner"])

    # Add emoji detection pipeline
    nlp.add_pipe("emoji", first=True)

    matcher = Matcher(nlp.vocab, validate=True)
    dep_matcher = DependencyMatcher(nlp.vocab, validate=True)
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER",
                                   validate=True)

    matcher_features = {k for k in rules["Matcher"].keys()}
    for rulename, rule in rules["Matcher"].items():
        matcher.add(rulename, rule["rules"])

    dep_features = {k for k in rules["DependencyMatcher"].keys()}
    for rulename, rule in rules["DependencyMatcher"].items():
        dep_matcher.add(rulename, rule["rules"])

    phrase_features = {k for k in rules["PhraseMatcher"].keys()}
    for rulename, rule in rules["PhraseMatcher"].items():
        phrase_matcher.add(rulename, list(nlp.tokenizer.pipe(rule["rules"])))

    return Matchers(nlp, matcher, dep_matcher, phrase_matcher,
                    matcher_features | dep_features | phrase_features)


def match_text(matchers, text):
    """Apply the matchers to a text string.

    Returns a dictionary of Matcher, DependencyMatcher, and PhraseMatcher matches.
    """

    doc = matchers.nlp(text)

    return {
        "Document": doc,
        "Matcher": matchers.plain(doc, as_spans=True),
        "DependencyMatcher": matchers.dependency(doc),
        "PhraseMatcher": matchers.phrase(doc, as_spans=True)
    }

def count_matches(matchers, matches):
    """Count the matches of each feature.

    Takes the output of match_text() and produces a dictionary of {feature_name:
    count} pairs.

    """

    matches_out = defaultdict(lambda: 0)

    for m in matches["Matcher"]:
        matches_out[m.label_] += 1

    for match_id, token_id in matches["DependencyMatcher"]:
        matches_out[matchers.nlp.vocab.strings[match_id]] += 1

    for m in matches["PhraseMatcher"]:
        matches_out[m.label_] += 1

    return matches_out

def count_matches_texts(matchers, doc_ids, texts):
    """Apply matchers to a sequence of documents.

    Returns a Pandas data frame. Each row is one document; each column is one
    matched feature. Entries are counts of each feature.

    """

    assert len(doc_ids) == len(texts), \
        "Number of doc_ids doesn't match number of texts"

    match_counts = [count_matches(matchers, match_text(matchers, text))
                    for text in texts]

    out = pd.DataFrame.from_records(match_counts, index=doc_ids).fillna(0)

    # If we didn't match a feature, add a column of 0s instead of omitting it
    # from the data frame
    missing_cols = matchers.feature_names - set(out.columns)

    for col in missing_cols:
        out[col] = 0

    return out

def print_matches(matchers, matches):
    def print_dict(d):
        for label, items in d.items():
            out = "; ".join(items)
            print(f"{label}: {out}")

    print("Matcher")
    matcher_matches = defaultdict(list)
    for m in matches["Matcher"]:
        matcher_matches[m.label_].append(m.text)

    print_dict(matcher_matches)

    print("DependencyMatcher")
    dep_matches = defaultdict(list)
    for match_id, token_ids in matches["DependencyMatcher"]:
        match_tokens = ", ".join(matches["Document"][t].text for t in token_ids)
        dep_matches[matchers.nlp.vocab.strings[match_id]].append(match_tokens)

    print_dict(dep_matches)

    print("PhraseMatcher")
    phrase_matches = defaultdict(list)
    for m in matches["PhraseMatcher"]:
        phrase_matches[m.label_].append(m.text)

    print_dict(phrase_matches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match a text against a JSON ruleset.")
    parser.add_argument("--model", help="spaCy model to use", default="en_core_web_sm")
    parser.add_argument("ruleset")
    parser.add_argument("text")

    args = parser.parse_args()

    ruleset = open(args.ruleset, "r")
    rules = json.load(ruleset)

    matchers = initialize_matchers(rules, args.model)
    matches = match_text(matchers, args.text)

    print_matches(matchers, matches)

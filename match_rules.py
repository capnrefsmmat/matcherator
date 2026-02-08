"""Match a text against rules."""

import argparse
import json

import spacy
from spacy.matcher import Matcher, DependencyMatcher

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match a text against a JSON ruleset.")
    parser.add_argument("--model", help="spaCy model to use", default="en_core_web_sm")
    parser.add_argument("ruleset")
    parser.add_argument("text")

    args = parser.parse_args()

    ruleset = open(args.ruleset, "r")
    rules = json.load(ruleset)

    nlp = spacy.load(args.model)
    matcher = Matcher(nlp.vocab, validate=True)
    dep_matcher = DependencyMatcher(nlp.vocab, validate=True)

    for rulename, rule in rules["Matcher"].items():
        matcher.add(rulename, rule)

    for rulename, rule in rules["DependencyMatcher"].items():
        dep_matcher.add(rulename, rule)

    doc = nlp(args.text)

    matches = matcher(doc, as_spans=True)
    for m in matches:
        print(f"{m.label_}: {m.text}")

    dep_matches = dep_matcher(doc)
    for match_id, token_ids in dep_matches:
        print(nlp.vocab.strings[match_id],
              ", ".join([doc[tok].text for tok in token_ids]))

"""Match a text against rules."""

import argparse
import json
from collections import defaultdict, namedtuple

import spacy
import pandas as pd

import matcherator.biber

def print_matches(doc):
    def stringify_match(m):
        if isinstance(m, tuple):
            # span of (begin, end) tokens
            begin, end = m
            return doc[begin:end].text

        # must be a list of token IDs
        return ", ".join(doc[t].text for t in m)

    for feature, matches in doc._.matcherator_biber.items():
        out = "; ".join([stringify_match(m) for m in matches])
        print(f"{feature}: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match a text against a JSON ruleset.")
    parser.add_argument("--model", help="spaCy model to use", default="en_core_web_sm")
    parser.add_argument("text")

    args = parser.parse_args()

    # no need for named-entity recognition
    nlp = spacy.load(args.model, disable=["ner"])

    # Add emoji detection pipeline
    nlp.add_pipe("emoji", first=True)

    # Add matcherator pipeline
    nlp.add_pipe("matcherator_biber")

    doc = nlp(args.text)

    print_matches(doc)

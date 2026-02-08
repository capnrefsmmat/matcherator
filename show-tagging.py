"""For a given text, print spaCy's part-of-speech and dependency parsing."""

import argparse

import spacy
from tabulate import tabulate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show tagging for a text")
    parser.add_argument("--model", help="spaCy model to use", default="en_core_web_sm")
    parser.add_argument("text", nargs="+")

    args = parser.parse_args()

    text = " ".join(args.text)

    nlp = spacy.load(args.model)

    doc = nlp(text)

    table = [[token.text, token.lemma_, token.pos_, token.tag_, token.dep_]
             for token in doc]

    print(tabulate(table, headers=["Text", "Lemma", "POS", "TAG", "DEP"]))

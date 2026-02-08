"""Display dependency parse graphically."""

import argparse

import spacy
from spacy import displacy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show dependency diagram.")

    parser.add_argument("--model", default="en_core_web_sm")
    parser.add_argument("text")

    args = parser.parse_args()

    nlp = spacy.load(args.model)
    doc = nlp(args.text)
    displacy.serve(doc, style="dep", auto_select_port=True)

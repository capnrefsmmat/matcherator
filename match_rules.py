"""Match a text against rules."""

import argparse
import json
from collections import namedtuple

import spacy
from spacy.matcher import Matcher, DependencyMatcher, PhraseMatcher

Matchers = namedtuple("Matchers", ["nlp", "plain", "dependency", "phrase"])

def initialize_matchers(rules, model):
    """Initialize matchers from a rule specification.

    The rule spec is read from the JSON rule file. We then initialize spaCy
    matchers and load the rules. Returns the three matchers (Matcher,
    DependencyMatcher, and PhraseMatcher) in a namedtuple.
    """

    nlp = spacy.load(model)
    matcher = Matcher(nlp.vocab, validate=True)
    dep_matcher = DependencyMatcher(nlp.vocab, validate=True)
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER",
                                   validate=True)

    for rulename, rule in rules["Matcher"].items():
        matcher.add(rulename, rule["rules"])

    for rulename, rule in rules["DependencyMatcher"].items():
        dep_matcher.add(rulename, rule["rules"])

    for rulename, rule in rules["PhraseMatcher"].items():
        phrase_matcher.add(rulename, list(nlp.tokenizer.pipe(rule["rules"])))

    return Matchers(nlp, matcher, dep_matcher, phrase_matcher)


def match_text(matchers, text):
    """Apply the matchers to a text string.

    Returns a dictionary of Matcher, DependencyMatcher, and PhraseMatcher matches.
    """

    doc = matchers.nlp(text)

    return {
        "Matcher": matchers.plain(doc, as_spans=True),
        "DependencyMatcher": matchers.dependency(doc),
        "PhraseMatcher": matchers.phrase(doc, as_spans=True)
    }


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

    print("Matcher")
    for m in matches["Matcher"]:
        print(f"{m.label_}: {m.text}")

    print("DependencyMatcher")
    for match_id, token_ids in matches["DependencyMatcher"]:
        print(matchers.nlp.vocab.strings[match_id])

    print("PhraseMatcher")
    for m in matches["PhraseMatcher"]:
        print(f"{m.label_}: {m.text}")

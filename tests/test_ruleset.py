"""Test rule files to ensure the examples and counterexamples match correctly."""

from .. import match_rules

import itertools
import json
import pytest
import os.path

import spacy

RULE_FILES = ["pseudobiber.json", "llm-patterns.json"]
MODEL = "en_core_web_sm"

def check_rule_in_spans(rulename, matches):
    for m in matches:
        if m.label_ == rulename:
            return True

    return False

def check_rule_in_matches(rulename, matches, nlp):
    for match_id, _ in matches:
        if nlp.vocab.strings[match_id] == rulename:
            return True

    return False


def test_examples(subtests):
    for rule_file in RULE_FILES:
        rule_path = os.path.join("./rules/", rule_file)

        rules = json.load(open(rule_path, "r"))

        nlp = spacy.load(MODEL, disable=["ner"])

        # Add emoji detection pipeline
        nlp.add_pipe("emoji", first=True)

        # Add matcherator pipeline
        nlp.add_pipe("matcherator", config={"path": rule_path})

        for rulename, rule in itertools.chain(rules["Matcher"].items(),
                                              rules["DependencyMatcher"].items(),
                                              rules["PhraseMatcher"].items()):
            with subtests.test(rulename):
                for example in rule.get("examples", []):
                    doc = nlp(example)

                    assert len(doc._.matcherator[rulename]) > 0, \
                        f"Expected `{rulename}` to match `{example}`"

                for example in rule.get("counterexamples", []):
                    doc = nlp(example)

                    assert len(doc._.matcherator[rulename]) == 0, \
                        f"Expected `{rulename}` to not match `{example}`"

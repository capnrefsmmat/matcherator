"""Test rule files to ensure the examples and counterexamples match correctly."""

import importlib.resources
import itertools
import json
import pytest

import spacy

import matcherator.biber
import matcherator.generic

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

def check_rule_examples(nlp, rules, attr_name, subtests):
    for rulename, rule in itertools.chain(rules["Matcher"].items(),
                                          rules["DependencyMatcher"].items(),
                                          rules["PhraseMatcher"].items(),
                                          rules["Derived"].items()):
        with subtests.test(rulename):
            for example in rule.get("examples", []):
                doc = nlp(example)

                assert len(getattr(doc._, attr_name)[rulename]) > 0, \
                    f"Expected `{rulename}` to match `{example}`"

            for example in rule.get("counterexamples", []):
                doc = nlp(example)

                assert len(getattr(doc._, attr_name)[rulename]) == 0, \
                    f"Expected `{rulename}` to not match `{example}`"

def test_biber(subtests):
    rules = json.loads(
        importlib.resources.files("matcherator.rules") \
        .joinpath("pseudobiber.json") \
        .read_text()
    )

    nlp = spacy.load(MODEL, disable=["ner"])

    # Add emoji detection pipeline
    nlp.add_pipe("emoji", first=True)

    # Add matcherator pipeline
    nlp.add_pipe("matcherator_biber")

    check_rule_examples(nlp, rules, "matcherator_biber", subtests)

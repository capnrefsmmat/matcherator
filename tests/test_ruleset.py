"""Test rule files to ensure the examples and counterexamples match correctly."""

from .. import match_rules

import json
import pytest
import os.path

RULE_FILES = ["pseudobiber.json"]
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
        rules = json.load(open(os.path.join("./rules/", rule_file), "r"))

        matchers = match_rules.initialize_matchers(rules, MODEL)

        for rulename, rule in rules["Matcher"].items():
            with subtests.test(f"Matcher: {rulename}"):
                for example in rule.get("examples", []):
                    matches = match_rules.match_text(matchers, example)

                    assert check_rule_in_spans(rulename, matches["Matcher"]), \
                        f"Expected rule `{rulename}` to match `{example}`"

                for example in rule.get("counterexamples", []):
                    matches = match_rules.match_text(matchers, example)

                    assert not check_rule_in_spans(rulename, matches["Matcher"]), \
                        f"Expected rule `{rulename}` to not match `{example}`"

        for rulename, rule in rules["DependencyMatcher"].items():
            with subtests.test(f"DependencyMatcher: {rulename}"):
                for example in rule.get("examples", []):
                    matches = match_rules.match_text(matchers, example)

                    assert check_rule_in_matches(rulename, matches["DependencyMatcher"], matchers.nlp), \
                        f"Expected rule `{rulename}` to match `{example}`"

                for example in rule.get("counterexamples", []):
                    matches = match_rules.match_text(matchers, example)

                    assert not check_rule_in_matches(rulename, matches["DependencyMatcher"], matchers.nlp), \
                        f"Expected rule `{rulename}` to not match `{example}`"

        for rulename, rule in rules["PhraseMatcher"].items():
            with subtests.test(f"PhraseMatcher: {rulename}"):
                for example in rule.get("examples", []):
                    matches = match_rules.match_text(matchers, example)

                    assert check_rule_in_spans(rulename, matches["PhraseMatcher"]), \
                        f"Expected rule `{rulename}` to match `{example}`"

                for example in rule.get("counterexamples", []):
                    matches = match_rules.match_text(matchers, example)

                    assert not check_rule_in_spans(rulename, matches["PhraseMatcher"]), \
                        f"Expected rule `{rulename}` to not match `{example}`"

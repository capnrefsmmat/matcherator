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


def test_examples():
    for rule_file in RULE_FILES:
        rules = json.load(open(os.path.join("../rules/", rule_file), "r"))

        matchers = match_rules.initialize_matchers(rules, MODEL)

        for rulename, rule in rules["Matcher"].items():
            for example in rule.get("examples", []):
                matches = match_rules.match_text(matchers, example)

                assert check_rule_in_spans(rulename, matches["Matcher"]), \
                    f"Matcher: Expected rule `{rulename}` to match `{example}`"

            for example in rule.get("counterexamples", []):
                matches = match_rules.match_text(matchers, example)

                assert not check_rule_in_spans(rulename, matches["Matcher"]), \
                    f"Matcher: Expected rule `{rulename}` to not match `{example}`"

        for rulename, rule in rules["DependencyMatcher"].items():
            for example in rule.get("examples", []):
                matches = match_rules.match_text(matchers, example)

                assert check_rule_in_matches(rulename, matches["DependencyMatcher"], matchers.nlp), \
                    f"DependencyMatcher: Expected rule `{rulename}` to match `{example}`"

            for example in rule.get("counterexamples", []):
                matches = match_rules.match_text(matchers, example)

                assert not check_rule_in_matches(rulename, matches["DependencyMatcher"], matchers.nlp), \
                    f"DependencyMatcher: Expected rule `{rulename}` to not match `{example}`"

        for rulename, rule in rules["PhraseMatcher"].items():
            for example in rule.get("examples", []):
                matches = match_rules.match_text(matchers, example)

                assert check_rule_in_spans(rulename, matches["PhraseMatcher"]), \
                    f"PhraseMatcher: Expected rule `{rulename}` to match `{example}`"

            for example in rule.get("counterexamples", []):
                matches = match_rules.match_text(matchers, example)

                assert not check_rule_in_spans(rulename, matches["PhraseMatcher"]), \
                    f"PhraseMatcher: Expected rule `{rulename}` to not match `{example}`"

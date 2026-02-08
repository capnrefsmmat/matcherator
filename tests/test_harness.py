import argparse
import json
import unittest
import spacy
from spacy.matcher import Matcher, DependencyMatcher
import os

class TestMatcherRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the rules
        rules_path = os.path.join(os.path.dirname(__file__), "../rules/pseudobiber.json")
        with open(rules_path, "r") as f:
            cls.rules = json.load(f)

        # Load the test cases
        cases_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
        with open(cases_path, "r") as f:
            cls.test_cases = json.load(f)

        # Initialize spaCy
        cls.nlp = spacy.load("en_core_web_sm")

        # Initialize matchers
        cls.matcher = Matcher(cls.nlp.vocab, validate=True)
        cls.dep_matcher = DependencyMatcher(cls.nlp.vocab, validate=True)

        for rulename, rule in cls.rules.get("Matcher", {}).items():
            cls.matcher.add(rulename, rule)

        for rulename, rule in cls.rules.get("DependencyMatcher", {}).items():
            cls.dep_matcher.add(rulename, rule)

    def test_rules(self):
        for case in self.test_cases:
            text = case["text"]
            should_match = set(case.get("should_match", []))
            should_not_match = set(case.get("should_not_match", []))

            with self.subTest(text=text):
                doc = self.nlp(text)

                # Collect all matches
                matches = self.matcher(doc, as_spans=True)
                found_matches = {m.label_ for m in matches}

                dep_matches = self.dep_matcher(doc)
                found_matches.update(self.nlp.vocab.strings[match_id] for match_id, token_ids in dep_matches)

                # Check for expected matches
                missing_matches = should_match - found_matches
                self.assertFalse(missing_matches, f"Expected matches not found in '{text}': {missing_matches}")

                # Check for unexpected matches
                unexpected_matches = should_not_match.intersection(found_matches)
                self.assertFalse(unexpected_matches, f"Unexpected matches found in '{text}': {unexpected_matches}")

if __name__ == "__main__":
    unittest.main()

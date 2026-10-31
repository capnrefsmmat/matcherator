"""Test rule files to ensure the examples and counterexamples match correctly."""

import importlib.resources
import json
import pytest

import spacy

import matcherator.biber, matcherator.generic
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

def check_examples(rule, label, get_matches, subtests):
    for example in rule.get("examples", []):
        with subtests.test(label + " examples"):
            assert len(get_matches(example)[label]) > 0, \
                f"Expected `{label}` to match `{example}`"

    for example in rule.get("counterexamples", []):
        with subtests.test(label + " counterexamples"):
            assert len(get_matches(example)[label]) == 0, \
                f"Expected `{label}` to not match `{example}`"

def check_rule_examples(nlp, rules, pipe_name, subtests):
    """Check examples and counterexamples for each feature and subrule.

    Feature examples are checked against the feature's final matches, after any
    post-processing. Subrule examples are checked against the matches of that
    subrule alone, before post-processing.

    """
    pipe = nlp.get_pipe(pipe_name)

    def feature_matches(text):
        return getattr(nlp(text)._, pipe_name)

    def subrule_matches(text):
        return pipe._match(nlp(text), keep_subrules=True)

    for feature_name, feature in rules.items():
        check_examples(feature, feature_name, feature_matches, subtests)

        for subrule_name, subrule in feature.get("subrules", {}).items():
            check_examples(subrule, f"{feature_name}:{subrule_name}",
                           subrule_matches, subtests)

def test_biber(subtests):
    rules = json.loads(
        importlib.resources.files("matcherator.rules") \
        .joinpath("pseudobiber.json") \
        .read_text()
    )

    nlp = spacy.load(MODEL, disable=["ner"])

    # Add matcherator pipeline
    nlp.add_pipe("matcherator_biber")

    check_rule_examples(nlp, rules, "matcherator_biber", subtests)

def test_llm_patterns(subtests):
    rules = json.loads(
        importlib.resources.files("matcherator.rules") \
        .joinpath("llm-patterns.json") \
        .read_text()
    )

    nlp = spacy.load(MODEL, disable=["ner"])

    # Add matcherator pipeline
    nlp.add_pipe("matcherator_generic", config={"rules": rules})

    check_rule_examples(nlp, rules, "matcherator_generic", subtests)

def test_symbols(subtests):
    rules = json.loads(
        importlib.resources.files("matcherator.rules") \
        .joinpath("symbols.json") \
        .read_text()
    )

    nlp = spacy.load(MODEL, disable=["ner"])

    # Add emoji detection pipeline
    nlp.add_pipe("emoji", first=True)

    # Add matcherator pipeline
    nlp.add_pipe("matcherator_generic", config={"rules": rules})

    check_rule_examples(nlp, rules, "matcherator_generic", subtests)

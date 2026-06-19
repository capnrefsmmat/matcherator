"""Test Biber ruleset examples against pybiber."""

import pybiber as pb

import importlib.resources
import itertools
import json
import pytest

import polars as pl

import spacy

def counterexamples_match(processor, nlp, counterexamples, rulename):
    if len(counterexamples) == 0:
        return True

    corpus = pl.DataFrame({"doc_id": [f"counterexample_{i}" for i in range(len(counterexamples))],
                           "text": counterexamples})

    df_spacy = processor.process_corpus(corpus, nlp)
    df_biber = pb.biber(df_spacy, normalize=False, strict_be_main_verb=False)

    if rulename in df_biber.columns:
        failed_matches = df_biber.filter(pl.col(rulename) > 0)["doc_id"].to_list()

        assert len(failed_matches) == 0, \
            f"Rule `{rulename}` incorrectly matched {', '.join(failed_matches)}"

def examples_match(processor, nlp, examples, rulename):
    if len(examples) == 0:
        return True

    corpus = pl.DataFrame({"doc_id": [f"example_{i}" for i in range(len(examples))],
                           "text": examples})

    df_spacy = processor.process_corpus(corpus, nlp)
    df_biber = pb.biber(df_spacy, normalize=False, strict_be_main_verb=False)

    if rulename in df_biber.columns:
        failed_matches = df_biber.filter(pl.col(rulename) == 0)["doc_id"].to_list()

        assert len(failed_matches) == 0, \
            f"Rule `{rulename}` failed to match {', '.join(failed_matches)}"

def test_examples(subtests):
    rules = json.loads(importlib.resources.files("matcherator.rules") \
                       .joinpath("pseudobiber.json") \
                       .read_text())

    processor = pb.CorpusProcessor()
    nlp = spacy.load("en_core_web_sm")

    for rulename, rule in itertools.chain(rules["Matcher"].items(),
                                          rules["DependencyMatcher"].items(),
                                          rules["PhraseMatcher"].items()):
        with subtests.test(f"Matcher: {rulename}"):
            examples_match(processor, nlp, rule.get("examples", []), rulename)
            counterexamples_match(processor, nlp, rule.get("counterexamples", []), rulename)

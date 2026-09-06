"""Test text statistics."""

import spacy
import matcherator.text_stats

MODEL = "en_core_web_sm"
nlp = spacy.load(MODEL, disable=["ner"])

def test_noun_phrase_lengths():
    doc = nlp("The quick brown fox jumps over the lazy dog.")

    # "the quick brown fox" and "the lazy dog"
    assert matcherator.text_stats.noun_phrase_lengths(doc) == [4, 3]

    doc = nlp("")
    assert matcherator.text_stats.noun_phrase_lengths(doc) == []

"""Unit tests for matcherator visualization and audit tools."""

import os
from pathlib import Path
import pytest
import spacy

import matcherator
import matcherator.biber
import matcherator.generic
from matcherator.visualize import extract_doc_data, render, visualize, audit


MODEL = "en_core_web_sm"


@pytest.fixture(scope="module")
def nlp_biber():
    nlp = spacy.load(MODEL, disable=["ner"])
    nlp.add_pipe("matcherator_biber")
    return nlp


@pytest.fixture(scope="module")
def nlp_symbols():
    nlp = spacy.load(MODEL, disable=["ner"])
    nlp.add_pipe("emoji", first=True)
    nlp.add_pipe("matcherator_generic", config={"rules": "symbols.json"})
    return nlp


def test_extract_doc_data_biber(nlp_biber):
    text = "The quick brown fox jumps over the lazy dog."
    doc = nlp_biber(text)

    data = extract_doc_data(doc)

    assert data["text"] == text
    assert len(data["tokens"]) == len(doc)
    assert len(data["sentences"]) >= 1

    # Check token structure
    tok0 = data["tokens"][0]
    assert tok0["text"] == "The"
    assert "pos" in tok0
    assert "tag" in tok0
    assert "dep" in tok0
    assert "lemma" in tok0
    assert "matches" in tok0

    # Features found
    assert "f_03_present_tense" in data["features"]
    assert "f_40_adj_attr" in data["features"]
    assert "f_16_other_nouns" in data["features"]

    # Check feature structure
    feat_present = data["features"]["f_03_present_tense"]
    assert feat_present["match_count"] >= 1
    assert len(feat_present["matches"]) >= 1
    assert feat_present["matcher_type"] == "Matcher"
    assert feat_present["description"] != ""
    assert "color" in feat_present

    # Stats
    assert data["stats"]["total_tokens"] == len(doc)
    assert data["stats"]["total_matches"] > 0
    assert data["stats"]["distinct_features"] > 0


def test_extract_doc_data_dependency_match(nlp_biber):
    text = "The ball was thrown by John."
    doc = nlp_biber(text)

    data = extract_doc_data(doc)

    # In passive voice, f_18_by_passives should match
    assert "f_18_by_passives" in data["features"]
    passive_feat = data["features"]["f_18_by_passives"]
    assert passive_feat["match_count"] >= 1

    match_obj = passive_feat["matches"][0]
    assert match_obj["feature_name"] == "f_18_by_passives"
    assert len(match_obj["token_indices"]) >= 2
    # Ensure tokens link back to this match ID
    for tid in match_obj["token_indices"]:
        assert match_obj["id"] in data["tokens"][tid]["matches"]


def test_render_html(nlp_biber):
    text = "The quick brown fox jumps over the lazy dog."
    doc = nlp_biber(text)

    html_str = render(doc, title="Test Audit")

    assert "<!doctype html>" in html_str
    assert "Test Audit" in html_str
    assert "f_03_present_tense" in html_str
    assert "id=\"doc-data-json\"" in html_str
    assert "jumps" in html_str


def test_visualize_and_audit_file_output(nlp_biber, tmp_path):
    text = "I have written this sentence."
    doc = nlp_biber(text)

    out_file = tmp_path / "audit_output.html"
    result = visualize(doc, output_path=out_file, title="Perfect Aspect Audit")

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "Perfect Aspect Audit" in content
    assert "f_02_perfect_aspect" in content
    assert result == content

    # Test audit alias
    out_file2 = tmp_path / "audit_alias.html"
    result2 = audit(doc, output_path=out_file2)
    assert out_file2.exists()
    assert result2 == out_file2.read_text(encoding="utf-8")


def test_generic_matcher_visualization(nlp_symbols, tmp_path):
    text = "She said: count all the colons! 💩"
    doc = nlp_symbols(text)

    data = extract_doc_data(doc, rules="symbols.json")
    assert "colons" in data["features"]
    assert "exclamation_marks" in data["features"]
    assert "emoji" in data["features"]

    html_str = render(doc, rules="symbols.json")
    assert "colons" in html_str
    assert "exclamation_marks" in html_str
    assert "emoji" in html_str


def test_custom_dict_rules():
    nlp = spacy.load(MODEL, disable=["ner"])
    custom_rules = {
        "Matcher": {
            "custom_fox": {
                "description": "Matches fox",
                "rules": [[{"LOWER": "fox"}]],
                "examples": ["fox"],
            }
        },
        "DependencyMatcher": {},
        "PhraseMatcher": {},
        "Derived": {},
    }
    nlp.add_pipe("matcherator_generic", config={"rules": custom_rules})
    doc = nlp("A brown fox ran.")

    data = extract_doc_data(doc, rules=custom_rules)
    assert "custom_fox" in data["features"]
    assert data["features"]["custom_fox"]["description"] == "Matches fox"

    html_str = render(doc, rules=custom_rules)
    assert "custom_fox" in html_str
    assert "Matches fox" in html_str


def test_include_derived_flag(nlp_biber):
    text = "The quick brown fox jumps over the lazy dog."
    doc = nlp_biber(text)

    # When include_derived is False (default), intermediate rules like f_16_other_nouns:all are omitted
    data_clean = extract_doc_data(doc, include_derived=False)
    assert "f_16_other_nouns:all" not in data_clean["features"]
    assert "f_16_other_nouns" in data_clean["features"]

    # When include_derived is True, f_16_other_nouns:all should be present
    data_all = extract_doc_data(doc, include_derived=True)
    assert "f_16_other_nouns:all" in data_all["features"]


def test_derived_other_nouns_token_span(nlp_biber):
    text = "This paper interrogates"
    doc = nlp_biber(text)

    data = extract_doc_data(doc)
    assert "f_16_other_nouns" in data["features"]
    matches = data["features"]["f_16_other_nouns"]["matches"]

    # Match for 'paper' should only span token 1, not tokens 1 and 2
    paper_match = [m for m in matches if m["matched_text"] == "paper"]
    assert len(paper_match) == 1
    assert paper_match[0]["token_indices"] == [1]
    assert paper_match[0]["matched_text"] == "paper"


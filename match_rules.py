"""Match a text against rules."""

import argparse
import json
from collections import defaultdict, namedtuple

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span
from spacy.matcher import Matcher, DependencyMatcher, PhraseMatcher
from spacymoji import Emoji

import pandas as pd

Doc.set_extension("matcherator", default=None)

@Language.factory("matcherator", default_config={"path": None, "normalize": False})
def matcherator(nlp, name, path, normalize):
    return Matcherator(nlp, path, normalize)

class Matcherator:
    def __init__(self, nlp, path, normalize):
        # Set up matchers
        self.matcher = Matcher(nlp.vocab, validate=True)
        self.dep_matcher = DependencyMatcher(nlp.vocab, validate=True)
        self.phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER",
                                            validate=True)

        # Load rules
        if path is None:
            raise ValueError("No path to rules file provided")

        with open(path, "r") as ruleset:
            rules = json.load(ruleset)

        matcher_features = {k for k in rules["Matcher"].keys()}
        for rulename, rule in rules["Matcher"].items():
            self.matcher.add(rulename, rule["rules"], greedy="FIRST")

        dep_features = {k for k in rules["DependencyMatcher"].keys()}
        for rulename, rule in rules["DependencyMatcher"].items():
            self.dep_matcher.add(rulename, rule["rules"])

        phrase_features = {k for k in rules["PhraseMatcher"].keys()}
        for rulename, rule in rules["PhraseMatcher"].items():
            self.phrase_matcher.add(rulename, list(nlp.tokenizer.pipe(rule["rules"])))

        self.features = matcher_features | dep_features | phrase_features
        self.nlp = nlp

    def __call__(self, doc):
        matches = self.matcher(doc)
        dep_matches = self.dep_matcher(doc)
        phrase_matches = self.phrase_matcher(doc)

        doc._.matcherator = defaultdict(list)

        # note that everything we add to doc._ must be serializable if we're
        # going to use this in a parallel pipeline, since multiprocessing has to
        # serialize the data back to the main process. Span objects are not, so
        # we have to stick to token ranges or indices.
        for match_id, start, end in matches:
            doc._.matcherator[self.nlp.vocab.strings[match_id]].append((start, end))

        for match_id, token_ids in dep_matches:
            doc._.matcherator[self.nlp.vocab.strings[match_id]].append(token_ids)

        for match_id, start, end in phrase_matches:
            doc._.matcherator[self.nlp.vocab.strings[match_id]].append((start, end))

        return doc


def count_matches(doc, normalize=False):
    """Return dictionary of match counts for a Document.

    For a Document that has already been matched, iterate through the matches
    and produce a dictionary of counts of each match type. If normalize is True,
    normalize to rates per 1,000 tokens.

    """

    if normalize:
        return {name: len(value) / len(doc) * 1000
                for name, value
                in doc._.matcherator.items()}
    else:
        return {name: len(value)
                for name, value
                in doc._.matcherator.items()}


def count_matches_texts(model, rule_path, doc_ids, texts, normalize=False,
                        n_process=1):
    """Apply spaCy and the given rules to a set of texts and count matches.

    Returns a Pandas data frame with one row per document and one column per
    feature, whose entries give the count of matches of each feature in each
    document. If normalize is True, counts are normalized to rates per 1,000
    tokens.

    n_process sets the number of parallel processes to use in the spaCy
    pipeline. There is a high fixed cost to spawning processes, so only set this
    greater than 1 when there are many texts. Set to -1 to use all available
    cores.

    """

    # no need for named-entity recognition
    nlp = spacy.load(model, disable=["ner"])

    # Add emoji detection pipeline
    nlp.add_pipe("emoji", first=True)

    # Add matcherator pipeline
    nlp.add_pipe("matcherator", config={"path": rule_path})

    # Eliminate Nones in texts
    doc_ids = [doc_ids[ii]
               for ii in range(len(doc_ids))
               if texts[ii] is not None]
    texts = [t for t in texts if t is not None]

    match_counts = [count_matches(doc, normalize)
                    for doc in nlp.pipe(texts, n_process=n_process)]

    return pd.DataFrame.from_records(match_counts, index=doc_ids) \
                       .fillna(0) \
                       .rename_axis("doc_id")


def print_matches(nlp, doc):
    def stringify_match(m):
        if isinstance(m, tuple):
            # span of (begin, end) tokens
            begin, end = m
            return doc[begin:end].text

        # must be a list of token IDs
        return ", ".join(doc[t].text for t in m)

    for feature, matches in doc._.matcherator.items():
        out = "; ".join([stringify_match(m) for m in matches])
        print(f"{feature}: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match a text against a JSON ruleset.")
    parser.add_argument("--model", help="spaCy model to use", default="en_core_web_sm")
    parser.add_argument("ruleset")
    parser.add_argument("text")

    args = parser.parse_args()

    # no need for named-entity recognition
    nlp = spacy.load(args.model, disable=["ner"])

    # Add emoji detection pipeline
    nlp.add_pipe("emoji", first=True)

    # Add matcherator pipeline
    nlp.add_pipe("matcherator", config={"path": args.ruleset})

    doc = nlp(args.text)

    print_matches(nlp, doc)

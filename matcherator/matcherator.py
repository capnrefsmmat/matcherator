"""spaCy pipeline extension to apply pattern-matching rules to text."""

from collections import defaultdict

import pandas as pd

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span
from spacy.matcher import Matcher, DependencyMatcher, PhraseMatcher


class Matcherator:
    def __init__(self, nlp, rules):
        # Set up matchers
        self.matcher = Matcher(nlp.vocab, validate=True)
        self.dep_matcher = DependencyMatcher(nlp.vocab, validate=True)
        self.phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER",
                                            validate=True)

        for rulename, rule in rules["Matcher"].items():
            self.matcher.add(rulename, rule["rules"], greedy="FIRST")

        for rulename, rule in rules["DependencyMatcher"].items():
            self.dep_matcher.add(rulename, rule["rules"])

        for rulename, rule in rules["PhraseMatcher"].items():
            self.phrase_matcher.add(rulename, list(nlp.tokenizer.pipe(rule["rules"])))

        self.features = _collect_features(rules)
        self.nlp = nlp

    def _match(self, doc):
        match_matches = self.matcher(doc)
        dep_matches = self.dep_matcher(doc)
        phrase_matches = self.phrase_matcher(doc)

        matches = defaultdict(list)

        # note that everything we add to doc._ must be serializable if we're
        # going to use this in a parallel pipeline, since multiprocessing has to
        # serialize the data back to the main process. Span objects are not, so
        # we have to stick to token ranges or indices.
        for match_id, start, end in match_matches:
            matches[self.nlp.vocab.strings[match_id]].append((start, end))

        for match_id, token_ids in dep_matches:
            matches[self.nlp.vocab.strings[match_id]].append(token_ids)

        for match_id, start, end in phrase_matches:
            matches[self.nlp.vocab.strings[match_id]].append((start, end))

        return matches


def _collect_features(rules):
    """Collect all valid feature names from rules.

    Some rules are used to derive others and should not be in the output; these
    have `derived` set to True. Ignore these.

    """

    def collect_one(r):
        return {
            feature_name
            for feature_name in r.keys()
            if not r[feature_name].get("derived", False)
        }

    return (collect_one(rules["Matcher"]) |
            collect_one(rules["DependencyMatcher"]) |
            collect_one(rules["PhraseMatcher"]) |
            collect_one(rules["Derived"]))


def feature_counts(nlp, doc, normalize=False):
    """Return a dictionary of feature counts for a Document.

    The document `doc` must have already been analyzed through a spaCy pipeline
    containing one or more Matcherator counters. If `normalize` is True, counts
    are normalized to rates per 1,000 tokens.

    """

    matcherator_pipes = [p for p in nlp.pipe_names
                         if p.startswith("matcherator_")]

    if normalize:
        factor = 1000 / len(doc)
    else:
        factor = 1

    counts = {}
    for pipe in matcherator_pipes:
        matches = getattr(doc._, pipe)
        features = getattr(doc._, pipe + "_features")

        counts |= {name: len(matches[name]) * factor
                   for name in features}

    return counts


def feature_df(corpus, nlp, normalize=False, n_process=1):
    """Count the features in a data frame of texts.

    `corpus` must be a data frame with a `doc_id` column and a `text` column.
    The features will be counted in each row. `nlp` must be a spaCy object with
    one or more Matcherator pipelines enabled.

    If `normalize` is True, counts are normalized to rates per 1,000 tokens.

    Returns a data frame with a `doc_id` column and columns for each counted
    feature.

    n_process sets the number of parallel processes to use in the spaCy
    pipeline. There is a high fixed cost to spawning processes, so only set this
    greater than 1 when there are many texts. Set to -1 to use all available
    cores.

    """

    # Eliminate Nones in texts
    doc_ids = corpus["doc_id"].tolist()
    texts = corpus["text"].tolist()

    doc_ids = [doc_ids[ii]
               for ii in range(len(doc_ids))
               if texts[ii] is not None]
    texts = [t for t in texts if t is not None]

    counts = [feature_counts(nlp, doc, normalize)
              for doc in nlp.pipe(texts, n_process=n_process)]

    return pd.DataFrame.from_records(counts, index=doc_ids) \
                       .fillna(0) \
                       .rename_axis("doc_id")

"""spaCy pipeline to count Biber features."""

import json
import importlib.resources

import pandas as pd

from spacy.language import Language
from spacy.tokens import Doc

from .matcherator import Matcherator

class BiberMatcherator(Matcherator):
    def __init__(self, nlp):
        rule_text = importlib.resources.files("matcherator.rules") \
            .joinpath("pseudobiber.json") \
            .read_text()

        rules = json.loads(rule_text)

        if not Doc.has_extension("matcherator_biber"):
            Doc.set_extension("matcherator_biber", default=None)

        if not Doc.has_extension("matcherator_biber_features"):
            Doc.set_extension("matcherator_biber_features", default=set())

        super().__init__(nlp, rules)

    def _filter_passives(self, matches):
        """Produce f_17_agentless_passives from matched passives.

        Our rules match all passives and by-passives; from the set difference,
        we get agentless passives.

        """

        by_passive_verbs = {(m[0], m[1])
                            for m in matches["f_18_by_passives"]}

        agentless = [m for m in matches["f_17_agentless_passives:all"]
                     if (m[0], m[1]) not in by_passive_verbs]

        matches["f_17_agentless_passives"] = agentless

        return matches

    def _filter_that_deletion(self, doc, matches):
        """Produce f_60_that_deletion.

        We match subordinator clauses with or without "that", and separately
        match those with "that". "That" deletion is the clauses without.

        We also match subordinator clauses where it introduces a wh-clause
        instead. For example, "The rationale helps ensure that workers
        understand what they should do." matches our DependencyMatcher rules.
        Here "understand" it introduces a wh-question ("what they should do")
        and not a clause like "that it is bad."

        """


        subord_thats = {(m[0], m[1], m[2])
                        for m in matches["f_60_that_deletion:that"]}
        wh_clauses = {(m[0], m[1], m[2])
                      for m in matches["f_60_that_deletion:wh_clause"]}

        that_deleted = [m for m in matches["f_60_that_deletion:all"]
                        if (m[0], m[1], m[2]) not in subord_thats
                        and (m[0], m[1], m[2]) not in wh_clauses]

        matches["f_60_that_deletion"] = that_deleted

        return matches

    def __call__(self, doc):
        matches = self._match(doc)

        matches = self._filter_passives(matches)
        matches = self._filter_that_deletion(doc, matches)

        doc._.matcherator_biber = matches
        doc._.matcherator_biber_features = self.features

        return doc


@Language.factory("matcherator_biber",
                  assigns=["doc._.matcherator_biber"])
def matcherator_biber(nlp, name):
    return BiberMatcherator(nlp)


def biber_counts(doc, normalize=False):
    """Return a dictionary of Biber feature counts for a Document.

    The document `doc` must have already been analyzed through a spaCy pipeline
    containing `matcherator_biber`. If `normalize` is True, counts are
    normalized to rates per 1,000 tokens.
    """

    if normalize:
        n_tokens = len(doc)

        return {name: len(doc._.matcherator_biber[name]) / n_tokens * 1000
                for name in doc._.matcherator_biber_features}

    return {name: len(doc._.matcherator_biber[name])
            for name in doc._.matcherator_biber_features}


def biber_df(corpus, nlp, normalize=False, n_process=1):
    """Count the Biber features in a data frame of texts.

    `corpus` must be a data frame with a `doc_id` column and a `text` column.
    The features will be counted in each row. `nlp` must be a spaCy object with
    the `matcherator_biber` pipeline enabled.

    If `normalize` is True, counts are normalized to rates per 1,000 tokens.

    Returns a data frame with a `doc_id` column and columns for each counted
    Biber feature.

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

    counts = [biber_counts(doc, normalize)
              for doc in nlp.pipe(texts, n_process=n_process)]

    return pd.DataFrame.from_records(counts, index=doc_ids) \
                       .fillna(0) \
                       .rename_axis("doc_id")

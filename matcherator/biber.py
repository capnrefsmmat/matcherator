"""spaCy pipeline to count Biber features."""

import json
import importlib.resources

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

    def _filter_that_deletion(self, matches):
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
        matches = self._filter_that_deletion(matches)

        doc._.matcherator_biber = matches
        # _ attributes must be serializable; sets aren't, so use a list
        doc._.matcherator_biber_features = list(self.features)

        return doc


@Language.factory("matcherator_biber",
                  assigns=["doc._.matcherator_biber"])
def matcherator_biber(nlp, name):
    return BiberMatcherator(nlp)

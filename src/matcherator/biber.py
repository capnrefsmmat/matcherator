"""spaCy pipeline to count Biber features."""

import json
import importlib.resources

from spacy.language import Language
from spacy.tokens import Doc

import textacy.text_stats.diversity

from .matcherator import Matcherator

class BiberMatcherator(Matcherator):
    """Calculate features based on Biber's set of register features.

    Feature definitions are given in ``rules/pseudobiber.json`` and are based on
    Biber (1988), Variation across speech and writing, Cambridge University
    Press, Appendix II. Additional examples and clarification based on Le Foll
    and Shakir (2023), Multi-Feature Tagger of English,
    <https://github.com/mshakirDr/MFTE>.

    By default, the type-token ratio is computed using the entire document. The
    ``f_43_type_token`` feature can instead be computed with a different
    diversity statistic or on a subset of tokens by configuring the
    ``ttr_func``, ``ttr_token_limit``, and ``ttr_args`` parameters.

    :param nlp: spaCy NLP object to use; must be the same one used to process
      the documents.
    :param ttr_func: Function to use to calculate type-token ratio. Defaults to
      ``textacy.text_stats.diversity.ttr``, which calculates the Type-Token
      Ratio (number of types / number of words). Can use any function that takes
      a spaCy ``Doc`` object as its first argument, such as the other functions
      in the `textacy.text_stats.diversity
      <https://textacy.readthedocs.io/en/latest/api_reference/text_stats.html#lexical-diversity-stats>`_
      module.
    :param ttr_token_limit: If ``None`` (the default), the TTR function is given
      all tokens. If an integer, only the first ``ttr_token_limit`` tokens are
      used to calculate the TTR.
    :param ttr_args: Optional dictionary of additional arguments to give to the
      ``ttr_func``. For example, if the function takes a ``variant`` argument to
      determine which version of TTR to use (as the default does),
      ``ttr_args={"variant": "root"}`` would select the desired variant.

    """
    def __init__(self, nlp, ttr_func, ttr_token_limit, ttr_args):
        rule_text = importlib.resources.files("matcherator.rules") \
            .joinpath("pseudobiber.json") \
            .read_text()

        rules = json.loads(rule_text)

        # Contains all matches
        if not Doc.has_extension("matcherator_biber"):
            Doc.set_extension("matcherator_biber", default=None)

        # Set of feature names corresponding to matches
        if not Doc.has_extension("matcherator_biber_features"):
            Doc.set_extension("matcherator_biber_features", default=set())

        # Statistics computed by calculation on the whole text, not by matching.
        # Namely, f_43_type_token and f_44_mean_word_length
        if not Doc.has_extension("matcherator_biber_stats"):
            Doc.set_extension("matcherator_biber_stats", default=set())

        self.ttr_func = ttr_func
        self.ttr_token_limit = ttr_token_limit
        self.ttr_args = ttr_args

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

    def _filter_other_nouns(self, matches):
        """Produce f_16_other_nouns.

        "Other nouns" means nouns and proper nouns, except for gerunds and
        nominalizations.

        """

        nominalizations = {(m[0], m[1])
                   for m in matches["f_14_nominalizations"]}
        gerunds = {(m[0], m[1])
                   for m in matches["f_15_gerunds"]}

        other_nouns = [m for m in matches["f_16_other_nouns:all"]
                       if (m[0], m[1]) not in nominalizations
                       and (m[0], m[1]) not in gerunds]

        matches["f_16_other_nouns"] = other_nouns

        return matches

    def _filter_split_infinitive(self, matches):
        """Produce f_62_split_infinitive.

        Split infinitives have intervening words between "to" and the
        infinitive, which we check by counting tokens.

        """

        matches["f_62_split_infinitive"] = [
            [m[0], m[1]]
            for m in matches["f_62_split_infinitive"]
            if m[0] - m[1] > 1
        ]

        return matches

    def _filter_split_auxiliary(self, doc, matches):
        """Produce f_63_split_auxiliary.

        Split auxiliaries have intervening words between the auxiliary and the
        verb, which we check by counting tokens. We also ensure there is at
        least one adverb in between, so we don't count cases like "I don't mind"
        (where "n't" is in between the auxiliary "do" and verb "mind").

        """

        matches["f_63_split_auxiliary"] = [
            [m[0], m[1]]
            for m in matches["f_63_split_auxiliary"]
            if m[0] - m[1] > 1
            and any(doc[idx].pos_ == "ADV" for idx in range(m[1], m[0]))
        ]

        return matches

    def _compute_mean_word_length(self, doc):
        """Mean word length, excluding digits and URLs."""
        lengths = [len(token.text)
                   for token in doc
                   if not token.is_punct
                   and not token.is_digit
                   and not token.like_url]

        if len(lengths) == 0:
            # No valid tokens
            return None

        return sum(lengths) / len(lengths)

    def _compute_ttr(self, doc):
        """Type-token ratio based on a customizable TTR function."""
        if self.ttr_token_limit is not None and len(doc) > self.ttr_token_limit:
                doc = doc[:self.ttr_token_limit]

        return self.ttr_func(doc, **self.ttr_args)

    def __call__(self, doc):
        matches = self._match(doc)

        matches = self._filter_passives(matches)
        matches = self._filter_that_deletion(matches)
        matches = self._filter_other_nouns(matches)
        matches = self._filter_split_infinitive(matches)
        matches = self._filter_split_auxiliary(doc, matches)

        doc._.matcherator_biber = matches
        # _ attributes must be serializable; sets aren't, so use a list
        doc._.matcherator_biber_features = list(self.features)

        doc._.matcherator_biber_stats = {
            "f_43_type_token": self._compute_ttr(doc),
            "f_44_mean_word_length": self._compute_mean_word_length(doc)
        }

        return doc


@Language.factory("matcherator_biber",
                  default_config={"ttr_func": textacy.text_stats.diversity.ttr,
                                  "ttr_token_limit": None,
                                  "ttr_args": {}},
                  assigns=["doc._.matcherator_biber"])
def matcherator_biber(nlp, name, ttr_func, ttr_token_limit, ttr_args):
    return BiberMatcherator(nlp, ttr_func, ttr_token_limit, ttr_args)

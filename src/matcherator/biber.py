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

    Declared as a spaCy pipeline component called ``matcherator_biber``, which
    can be added to any pipeline::

      import spacy, matcherator.biber
      nlp = spacy.load("en_core_web_sm", disable=["ner"])
      nlp.add_pipe("matcherator_biber")

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

    def _filter_that_deletion(self, doc, matches):
        """Produce f_60_that_deletion.

        The DependencyMatcher rule matches every verb in the specified classes
        with a clausal complement, as (verb, complement verb). "That" deletion
        is the finite complement clauses with a subject but no "that", so we
        remove clauses with "that" or another subordinator, to-infinitives,
        wh-clauses, quotations, and clauses that come before the verb.

        """

        def keep(verb, comp):
            auxiliaries = [c for c in comp.children if c.dep_ in ("aux", "auxpass")]

            # No subject, so not a clause. Existential "there" counts, and
            # spaCy sometimes attaches the subject to the auxiliary.
            subjects = [c for c in comp.children
                        if c.dep_ in ("nsubj", "nsubjpass", "expl")] + \
                [c for a in auxiliaries for c in a.children
                 if c.dep_ in ("nsubj", "nsubjpass", "expl")]
            if not subjects:
                return False

            # Non-finite small clause with no auxiliary: "found her mother gone"
            if comp.tag_ in ("VBN", "VBG") and not auxiliaries:
                return False

            # "That" or another subordinator is present: "I think that he
            # went", "She asked if he was coming"
            if any(c.dep_ == "mark" for c in comp.children):
                return False

            # To-infinitive, which can't take "that": "allows us to isolate"
            if any(c.tag_ == "TO" for c in comp.children):
                return False

            # Complement or subject before the verb: "He was right, I think",
            # "'It's a good idea,' he said"
            subject = subjects[0]
            if comp.i < verb.i or subject.i < verb.i:
                return False

            # Wh-clause, which can't take "that": a wh-word between the verb
            # and the clause's subject, or as the subject ("asked me what I
            # was watching", "understood what nourished his soul")
            if any(t.tag_ in ("WDT", "WP", "WP$", "WRB")
                   for t in doc[verb.i + 1:min(subject.i, comp.i) + 1]):
                return False

            # Quotation: "She said, 'It's a good idea.'"
            if any(c.tag_ == "``" for c in verb.children):
                return False

            return True

        matches["f_60_that_deletion"] = [
            m for m in matches["f_60_that_deletion"]
            if keep(doc[m[0]], doc[m[1]])
        ]

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
            m for m in matches["f_62_split_infinitive"]
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
            m for m in matches["f_63_split_auxiliary"]
            if m[0] - m[1] > 1
            and any(doc[idx].pos_ == "ADV" for idx in range(m[1], m[0]))
        ]

        return matches

    def _filter_wh_question(self, matches):
        """Produce f_13_wh_question.

        The DependencyMatcher rule generally performs well, but has false
        positives for sentences like "Was the issue ignored, when it is so
        important?" Where "when" is a WH-word and descends from "ignored", so
        the rule matches. We can distinguish this case because the WH word is
        *after* the verb; Biber et al. defines WH-questions to be when the
        clause *opens* with the WH word.

        """

        matches["f_13_wh_question"] = [
            m for m in matches["f_13_wh_question"]
            if m[2] < m[0]
        ]

        return matches

    def _filter_pied_piping(self, matches):
        """Produce f_33_pied_piping.

        The DependencyMatcher rule is effective, but in pied-piping, the
        preposition needs to precede the verb ("in whom you are interested", not
        "who you are interested in"). The rule has some false positives unless
        we filter these cases out.

        """

        matches["f_33_pied_piping"] = [
            m for m in matches["f_33_pied_piping"]
            if m[2] < m[1]
        ]

        return matches

    def _filter_sentence_relatives(self, doc, matches):
        """Produce f_34_sentence_relatives and exclude them from wh-relatives.

        Each subrule's first token is *which*. When the *which* clause is
        attached to a noun, we remove it if the noun's governing verb follows
        the clause, as in "The car, which runs poorly, was falling apart", or
        if its verb is plural, as sentence relatives take singular verbs. We
        also remove questions like "which of you...". Several subrules can
        match the same *which*, so we count each only once.

        Because spaCy often attaches sentence relatives to a preceding noun as
        an ordinary ``relcl``, we also remove any ``f_31_wh_subj`` or
        ``f_32_wh_obj`` matches whose *wh*-word was matched as a sentence
        relative.

        """

        def keep(which):
            # Question, not a relative clause: "which of you gets the
            # privilege?"
            if any(c.dep_ == "prep" for c in which.children):
                return False

            # Clause is not attached to a noun (e.g., attached to a verb, or
            # pied-piped "in which case"), so the noun checks don't apply
            verb = which.head
            if verb.dep_ != "relcl":
                return True

            # Plural verb, so *which* refers to a plural noun, not a clause:
            # "slingbacks, which weren't bad"
            verbs = [verb] + [c for c in verb.children if c.dep_ in ("aux", "auxpass")]
            if any(v.tag_ == "VBP" or v.lower_ == "were" for v in verbs):
                return False

            # Noun's governing verb follows the clause, so the clause modifies
            # the noun mid-sentence: "The car, which runs poorly, was falling
            # apart"
            following = [t for t in doc[verb.right_edge.i + 1:which.sent.end]
                         if not t.is_punct]
            if following:
                governor = following[0]
                if governor.dep_ in ("aux", "auxpass"):
                    governor = governor.head
                if governor in verb.head.ancestors:
                    return False

            # Attached to a noun but passed every check
            return True

        seen = set()
        sentence_relatives = []
        for m in matches["f_34_sentence_relatives"]:
            if m[0] not in seen and keep(doc[m[0]]):
                seen.add(m[0])
                sentence_relatives.append(m)

        matches["f_34_sentence_relatives"] = sentence_relatives

        matches["f_31_wh_subj"] = [
            m for m in matches["f_31_wh_subj"]
            if m[2] not in seen
        ]
        matches["f_32_wh_obj"] = [
            m for m in matches["f_32_wh_obj"]
            if m[2] not in seen
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
        matches = self._filter_that_deletion(doc, matches)
        matches = self._filter_other_nouns(matches)
        matches = self._filter_split_infinitive(matches)
        matches = self._filter_split_auxiliary(doc, matches)
        matches = self._filter_wh_question(matches)
        matches = self._filter_pied_piping(matches)
        matches = self._filter_sentence_relatives(doc, matches)

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

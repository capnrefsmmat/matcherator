"""spaCy pipeline extension to apply pattern-matching rules to text."""

from collections import defaultdict

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

"""Match against any ruleset.

Specific matchers, like `BiberMatcherator`, employ post-processing after the
matching to better match certain patterns. For rulesets where no post-processing
is required, generic matching is sufficient.

"""

import json
import importlib.resources

from spacy.language import Language
from spacy.tokens import Doc

from .matcherator import Matcherator

class GenericMatcherator(Matcherator):
    def __init__(self, nlp, rules):
        """Set up a generic matcher.

        `rules` can either be a dictionary containing the rules or the name of a
        JSON file of rules provided with matcherator`, such as
        `pseudobiber.json`.

        """

        if not isinstance(rules, dict):
            rule_text = importlib.resources.files("matcherator.rules") \
                .joinpath(rules) \
                .read_text()

            rules = json.loads(rule_text)

        if not Doc.has_extension("matcherator_generic"):
            Doc.set_extension("matcherator_generic", default=None)

        if not Doc.has_extension("matcherator_generic_features"):
            Doc.set_extension("matcherator_generic_features", default=set())

        super().__init__(nlp, rules)

    def __call__(self, doc):
        doc._.matcherator_generic = self._match(doc)
        doc._.matcherator_generic_features = self.features

        return doc


@Language.factory("matcherator_generic",
                  assigns=["doc._.matcherator_generic"])
def matcherator_generic(nlp, name, rules):
    return GenericMatcherator(nlp, rules)

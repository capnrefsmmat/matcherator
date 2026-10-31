Rulesets
--------

Each ruleset provides a set of lexical, grammatical, or rhetorical features that
can be automatically matched. Rules can be matched in several different ways:

* spaCy's `Matcher <https://spacy.io/api/matcher>`_ pattern-matches on sequences
  of token attributes.
* spaCy's `DependencyMatcher <https://spacy.io/api/dependencymatcher>`_
  pattern-matches on structures in the dependency trees.
* spaCy's `PhraseMatcher <https://spacy.io/api/phrasematcher>`_ matches exact
  words or phrases.
* Custom code can be written in each class to post-process these matches or to
  extract other features from the spaCy parsing data.

Built-in rule sets:

.. toctree::
   biber
   symbols
   text-statistics

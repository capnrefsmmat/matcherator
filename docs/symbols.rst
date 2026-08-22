Symbols
=======

The ``symbols.json`` rule file provides rules for matching a range of symbols
and punctuation.

Usage
-----

The generic matcher can match these rules, provided we add spacymoji's ``emoji``
pipeline first::

  import spacy
  import matcherator
  import matcherator.generic

  nlp = spacy.load("en_core_web_sm", disable=["ner"])
  nlp.add_pipe("emoji", first=True)
  nlp.add_pipe("matcherator_generic", config={"rules": "symbols.json"})

  doc = nlp("The quick brown fox jumps over the lazy dog!")
  doc._.matcherator_generic

  matcherator.feature_counts(nlp, doc)

Feature reference
-----------------

.. include:: symbols-reference.rst

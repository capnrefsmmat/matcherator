Biber features
==============

The ``pseudobiber.json`` rules file provides rules for matching Douglas Biber's
set of lexical, grammatical, and rhetorical features.

Usage
-----

The ``BiberMatcherator`` class is configured so it can be added directly as a
spaCy pipeline. For example::

  import spacy
  import matcherator
  import matcherator.biber

  nlp = spacy.load("en_core_web_sm", disable=["ner"])
  nlp.add_pipe("matcherator_biber")

  doc = nlp("The quick brown fox jumps over the lazy dog.")
  doc._.matcherator_biber # dictionary of all feature matches

If options must be provided, use the ``config`` argument to ``add_pipe()``::

  nlp.add_pipe("matcherator_biber",
               config={"ttr_token_limit": 100})

API
---

.. autoclass:: matcherator.biber::BiberMatcherator

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

Feature reference
-----------------

References
^^^^^^^^^^

* Rules based on Appendix II of Douglas Biber (1988). *Variation across speech
  and writing.* Cambridge University Press.
* For some examples and definitions used below: Quirk, Greenham, Leech, Svartvik
  (1985). *A Comprehensive Grammar of the English Language.* Longman.

Note that some rules show up twice under different matchers. In these cases, two
different strategies are used to find different cases of the pattern, then
combined when computing results.

.. include:: pseudobiber-reference.rst

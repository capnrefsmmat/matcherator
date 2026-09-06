Text statistics
===============

The ``matcherator_text_stats`` pipeline provided in ``matcherator.text_stats``
computes various numerical summaries of readability and structure.

Usage
-----

The ``TextStats`` class is configured so it can be added directly as a spaCy
pipeline. For example::

  import spacy
  import matcherator
  import matcherator.text_stats

  nlp = spacy.load("en_core_web_sm", disable=["ner"])
  nlp.add_pipe("matcherator_text_stats")

  doc = nlp("The quick brown fox jumps over the lazy dog.")
  doc._.matcherator_text_stats_stats # dictionary of all feature matches

  # alternately, dictionary of all features across all loaded pipelines:
  matcherator.feature_counts(nlp, doc)

API
---

.. autoclass:: matcherator.text_stats::TextStats

Feature reference
-----------------

The computed text statistics are based on those provided by the `textacy package
<https://textacy.readthedocs.io/en/latest/index.html>`_.

:mean_noun_phrase_len: Mean length (in words) of noun phrases in the text, based
                       on the dependency parsed structure and spaCy's
                       `Doc.noun_chunks
                       <https://spacy.io/api/doc#noun_chunks>`_. For example, in
                       "the quick brown fox jumps over the lazy dog", "the quick
                       brown fox" and "the lazy dog" are the two noun phrases.
:mean_sentence_len: Mean length (in words) of sentences in the text, using the
                    sentence splitting determined by spaCy's dependency parsing.
:flesch_reading_ease: The Flesch Reading Ease of the text, which uses word
                      length and sentence length to compute a simple readability
                      score. High scores are more "readable".

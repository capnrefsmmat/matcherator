Functions for matching
======================

To quickly match features in texts, it's sufficient to create a spaCy pipeline
with the right matcherator rules added::

  import spacy
  import matcherator
  import matcherator.biber

  nlp = spacy.load("en_core_web_sm", disable=["ner"])
  nlp.add_pipe("matcherator_biber")

Then either of the functions below can return feature counts in a convenient
format.

.. autofunction:: matcherator.feature_counts

.. autofunction:: matcherator.feature_df

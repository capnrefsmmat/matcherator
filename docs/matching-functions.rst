Functions for matching
======================

To quickly match features in texts, it's sufficient to create a spaCy pipeline
with the right matcherator pipelines added::

  import spacy
  import matcherator
  import matcherator.biber, matcherator.text_stats

  nlp = spacy.load("en_core_web_sm", disable=["ner"])
  nlp.add_pipe("matcherator_biber")
  nlp.add_pipe("matcherator_text_stats")

You can load one pipeline or several. Then either of the functions below can
return feature counts from all loaded pipelines in a convenient format.

.. autofunction:: matcherator.feature_counts

.. autofunction:: matcherator.feature_df

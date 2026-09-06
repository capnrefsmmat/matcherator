"""spaCy pipeline to compute aggregate structural statistics in text."""

import statistics
import textacy.text_stats

from spacy.language import Language
from spacy.tokens import Doc

from .matcherator import Matcherator

class TextStats:
    """Calculate textual statistics on documents.

    Uses the textacy package to compute simple statistics, such as Flesch
    Reading Ease and mean word length.

    Declared as a spaCy pipeline component called ``matcherator_text_stats``,
    which can be added to any pipeline::

      import spacy, matcherator.text_stats
      nlp = spacy.load("en_core_web_sm", disable=["ner"])
      nlp.add_pipe("matcherator_text_stats")

    :param nlp: spaCy NLP object to use; must be the same one used to process
      the documents.

    """

    def __init__(self, nlp):
        if not Doc.has_extension("matcherator_text_stats"):
            Doc.set_extension("matcherator_text_stats", default={})

        if not Doc.has_extension("matcherator_text_stats_stats"):
            Doc.set_extension("matcherator_text_stats_stats", default={})

        if not Doc.has_extension("matcherator_text_stats_features"):
            Doc.set_extension("matcherator_text_stats_features", default=set())

    def __call__(self, doc):
        nplens = noun_phrase_lengths(doc)
        if len(nplens) > 0:
            mean_nplens = statistics.mean(nplens)
        else:
            mean_nplens = None

        doc._.matcherator_text_stats_stats = {
            "mean_noun_phrase_len": mean_nplens,
            "mean_sentence_len": mean_sentence_length(doc),
            "flesch_reading_ease": textacy.text_stats.readability.flesch_reading_ease(doc)
        }

        return doc


@Language.factory("matcherator_text_stats",
                  assigns=["doc._.matcherator_text_stats"])
def matcherator_text_stats(nlp, name):
    return TextStats(nlp)

def noun_phrase_lengths(doc):
    return [len(c) for c in doc.noun_chunks]

def mean_sentence_length(doc):
    n_words = textacy.text_stats.basics.n_words(doc)
    n_sents = textacy.text_stats.basics.n_sents(doc)

    if n_sents > 0:
        return n_words / n_sents

    return None

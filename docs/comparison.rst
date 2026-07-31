Comparison to other taggers
===========================

There are several widely used packages for tagging lexicogrammatical features in
text, particularly the Biber features:

* The original Biber Tagger, developed to support Biber's original work in the
  1980s and subsequently extended. Howeer, this is not publicly available.
* `biberpy <https://github.com/ssharoff/biberpy>`_, by Serge Sharoff, a Python
  script which takes texts already lemmatized and POS-tagged and calculates most
  of Biber's rules.
* The `Multidimensional Analysis Tagger
  <https://sites.google.com/site/multidimensionaltagger>`_, a Perl-based GUI,
  which uses the Stanford Tagger for POS tagging and again implements Biber's
  feature rules.
* `BiberPlus <https://github.com/davidjurgens/biberplus>`_, a Python package
  that uses spaCy to do POS-tagging and then applies Biber's rules on top.
* The `Multi-Feature Tagger of English <https://github.com/mshakirDr/MFTE>`_, a
  Python package using Stanza for POS-tagging to calculate an expanded set of
  features derived from Biber's.
* `pseudobibeR <https://cran.r-project.org/package=pseudobibeR>`_ (R) and
  `pybiber <https://browndw.github.io/pybiber/>`_ (Python), parallel
  implementations by the same author that use spaCy tagging and calculate
  Biber's features.

Why write a new tagger? The main motivation is *how* the features are detected.
The taggers above rely on rules based on sequences of tokens in texts, checking
for certain words of one type followed by words of other types in various
sequences. For example, here is how BiberPlus documents its function for finding
*that* relative clauses on object position::

  def tag_tobj(self, word, previous_words, next_words):
    """ That relative clauses on object position. Criteria:
        - The word is 'that'.
        - Preceded by a noun.
        - Followed by one of: determiner, subject form of a personal pronoun,
          possessive pronoun, the pronoun 'it', an adjective, plural noun,
          proper noun, or possessive noun. """

The code follows this description, checking the words and their parts-of-speech.
But modern dependency parsers let us search the actual grammatical structure of
text using the `Universal Dependency Relations
<https://universaldependencies.org/u/dep/index.html>`_. For this rule, we want a
noun, a verb that is a ``relcl`` (relative clause) describing the noun, and a
*that* token that is the object of the verb. In spaCy's `DependencyMatcher
<https://spacy.io/api/dependencymatcher>`_ notation for patterns, that is::

  [
    {
      "RIGHT_ID": "noun_anchor",
      "RIGHT_ATTRS": {"POS": {"IN": ["PROPN", "NOUN"]}}
    },
    {
      "LEFT_ID": "noun_anchor",
      "REL_OP": ">",
      "RIGHT_ID": "rel_verb",
      "RIGHT_ATTRS": {"DEP": "relcl"}
    },
    {
      "LEFT_ID": "rel_verb",
      "REL_OP": ">",
      "RIGHT_ID": "that_token",
      "RIGHT_ATTRS": {"LOWER": "that", "DEP": {"IN": ["dobj", "pobj", "dative"]}}
    }
  ]

This rule works no matter what the actual sequence of tokens is, as long as
spaCy's dependency parser can correctly understand the structure of the
sentence.

Using this approach allows more reliable detection of many features. For
example, Biber's original rule for split infinitives was *to* + ADV + (ADV) +
VB. That is, *to*, one or two adverbs, and then a verb in base form, such as the
phrase *to boldly go*. The packages above largely replicate this logic. But it
would fail to detect a split infinitive like *to boldly and rapidly go*, because
*boldly and rapidly* is three tokens and the rule only allows up to two adverbs
between *to* and the verb.

Instead, we can use the dependency parse to find every *to* marked as an
auxiliary of a verb in base form::

  [
    {
      "RIGHT_ID": "verb_anchor",
      "RIGHT_ATTRS": {"TAG": "VB"}
    },
    {
      "LEFT_ID": "verb_anchor",
      "REL_OP": ">",
      "RIGHT_ID": "to",
      "RIGHT_ATTRS": {
        "TAG": "TO", "DEP": "aux"
      }
    }
  ]

Our code can then scan the matches and check if the *to* and the verb are more
than one token apart. This approach is more robust and detects split infinitives
other taggers cannot.

The matcherator uses these dependency-based rules for many features, but not
all. For example, detecting verbs in the past tense does not require any special
dependency relations, only the POS tags, so we use spaCy's `Matcher
<https://spacy.io/api/matcher>`_ rules, which allow matching tokens meeting
certain criteria. Matcher can also do regular-expression-style matching on
sequences of tokens, such as negation and repetition.

For rules that only require looking for certain words or phrases, we use
`PhraseMatcher <https://spacy.io/api/phrasematcher>`_, which can match sequences
of words or phrases directly.

By using spaCy's pattern-matching facilities, we thus gain the ability to
express more complete grammatical rules based on the actual dependency
structure, rather than using heuristics. We also benefit from any clever
pattern-matching algorithms built into spaCy that make the rules more efficient,
as well as benefiting from spaCy's facilities for parallel processing of large
corpora.

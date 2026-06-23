# matcherator: spaCy pattern-matching libraries

**Currently experimental.** This code uses spaCy's pattern-matching facilities
to match lexical, grammatical, and rhetorical features in texts to facilitate
corpus linguistic analyses.

The ultimate goal is to provide a package with several rulesets for different
features.

## Design

Match rules are defined in JSON format in `rules/`. `match_rules.py` can set up
a spaCy pipeline to apply these rules to texts. It can also be run at the
command line:

```sh
python match_rules.py rules/pseudobiber.json "The quick brown fox jumps over the lazy dog."
```

Unit tests work with pytest. Test data is defined in the same rule files, by
`examples` and `counterexamples` files for each rule: the rule must match the
`examples` and must not match the `counterexamples`.

`test/test_ruleset.py` uses these to test the matcherator matching engine and
rule definitions.

`test/test_pybiber.py` uses these examples to test pybiber. Many of these tests
are expected to fail, since pybiber's rules are not as flexible, or sometimes
are defined slightly differently.

## pseudobiber

Rules like Biber's.

Audit notes, comparing to pybiber/pseudobibeR:

- pybiber normalizes curly quotes to straight quotes, curly apostrophes to
  straight ones, and en/em-dashes to hyphens. This can sometimes change spaCy's
  dependency parsing.
- `f_01_past_tense` through `f_11_indefinite_pronouns`: match well, rules are
  simple.
- `f_12_proverb_do`: doesn't match pybiber due to [pybiber issue
  #8](https://github.com/browndw/pybiber/issues/8)
- `f_13_wh_question`, `f_14_nominalizations`: good
- `f_15_gerunds`: doesn't match pybiber due to [pybiber issue
  #7](https://github.com/browndw/pybiber/issues/7)
- `f_16_other_nouns`: pseudobibeR and pybiber filter out tokens containing "-",
  but I don't know why; should I replicate this?
- `f_17_agentless_passives` and `f_18_by_passives`: Good. In a parallel
  construction ("This was done by Steve rather than by Sharon"), the
  `DependencyMatcher` will count two by-passives, not one.
- `f_19_be_main_verb`: we try to replicate pybiber with `strict_be_main_verb =
  False`.
- `f_20_existential_there`: good
- `f_21_that_verb_comp`, `f_22_that_adj_comp`: We incorrectly match some clauses
  do to spaCy's tagging; pybiber incorrectly matches some because it is looking
  at a word sequence and not the dependency structure.
- `f_23_wh_clause`: TODO does not match pybiber at all. Need some more examples
  to understand what rule to write. I can do it with DependencyMatcher, but what
  dependency to look for? Dative comes up in the one example, but is that the
  right thing to match?
- `f_24_infinitives`: good
- For `f_25_present_participle` and `f_26_past_participle`, pseudobibeR requires
  the verb to start the sentence. But is that necessary? Consider "Joe ran out
  the door, stuffing his mouth with cookies." Is it instead sufficient just to
  get VBG/VBNs with advcl or ccomp relation?
  - It at least has to start the clause; see `f_26_past_participle` for
    counterexample when it doesn't start the sentence or clause.
- `f_27_past_participle_whiz` and `f_28_present_participle_whiz`: pybiber relies
  on the verb being immediately after the noun, but `DependencyMatcher` allows
  more complex construction (see examples).
- `f_27_past_participle_whiz`, `f_28_present_participle_whiz`, `f_29_that_subj`,
  `f_30_that_obj`: pybiber only looks for nouns, not proper nouns, so we detect
  additional cases.
- `f_31_wh_subj` and `f_32_wh_obj`: We detect cases like "Our sense of agency
  reflects what our cognitive systems believe about our control, *which* may
  diverge from objective reality." Here *which* is the subject of *diverge*. I'm
  not sure if this matches Biber's intent, but pybiber doesn't detect it.
- `f_33_pied_piping`: TODO Two examples that pybiber finds and we don't, and I'm
  not sure who's right:
  - "The contact angle at the three-phase line increases monotonically with
    applied pressure until reaching the critical advancing angle θa, at which
    point the energetic barrier to meniscus motion is overcome and the interface
    begins to advance."
  - "Brewin, Gregory, Lipton, and Burgess (2010) found that individuals with
    post-traumatic stress disorder, many of whom reported significant childhood
    adversity, exhibited elevated levels of OGM."
- `f_33_pied_piping`: pybiber and pseudobiber only look for the forms "in who",
  "in whom", "in whose", and "in which"; and not, for instance, "on which" or
  "to which", though those can be pied piping too.
- `f_34_sentence_relatives`: Match pybiber pretty well; we add a DEP constraint
  on "which" to be more specific. I'm not sure the rule is precise; it matches
  Biber's book, but probably we can do better with DependencyMatcher?
- `f_35_because`: pseudobibeR and pybiber forbid following "of". Necessary? Need
  test cases/examples. Their rules look just at word occurrence, but ours uses
  DependencyMatcher and explicitly looks for adverbial clauses.
- `f_36_though`, `f_37_if`, `f_38_other_adv_sub`: again, our rules are better.
  Particularly for `f_38_other_adv_sub`, since it allows many other
  subordinators, pybiber finds lots of cases that are not adverbial clauses.
- `f_39_prepositions`: good
- `f_40_adj_attr` and `f_41_adj_pred`: pybiber uses word order to distinguish
  attributive and predicative adjectives; we use spaCy's dependency parse.
- `f_42_adverbs`: pybiber does not count RBS (adverb, superlative); we do
- `f_43_type_token` and `f_44_mean_word_length`: TODO we do not yet implement
  these.
- `f_45_conjuncts`: We match pybiber fine, but I suspect there's a better
  DependencyMatcher rule we could use.
- `f_46_downtoners` through `f_59_contractions`: good
- `f_60_that_deletion`: good, though our approach is fancier than pybiber's
- `f_61_stranded_preposition`: Good, though I don't understand why pybiber
  doesn't get tripped up by hyphens
- `f_62_split_infinitive` and `f_63_split_auxiliary`: These simple patterns will
  miss obvious cases where the split is long. ("To boldly and proudly go
  where...") It'd be better to do it with DependencyMatcher. e.g., for split
  infinitives, match the `to` to the verb, and then in Python check if they're
  adjacent or not.
- `f_64_phrasal_coordination` and `f_65_clausal_coordination`: good, modulo
  spaCy tagging differences
- `f_66_neg_synthetic` and `f_66_neg_analytic`: good


## LLM patterns

Stylistic features reported to be common among LLMs, so that they can be
automatically detected and quantified. Does not replicate pseudobiber features
that mark AI writing---only includes features not counted by pseudobiber.

Sources for reported style features and examples:

- Wikipedia's [Signs of AI
  writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide
- [tropes.fyi](https://tropes.fyi/)
- sneak's [LLM Prose
  Tells](https://git.eeqj.de/sneak/prompts/src/branch/main/prompts/LLM_PROSE_TELLS.md)

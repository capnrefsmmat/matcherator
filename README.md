# matcherator: spaCy pattern-matching libraries

**Currently experimental.** This code uses spaCy's pattern-matching facilities
to match lexical, grammatical, and rhetorical features in texts to facilitate
corpus linguistic analyses.

The ultimate goal is to provide a package with several rulesets for different
features.

## pseudobiber

Rules like Biber's.

TODO notes:

- `f_16_other_nouns`: Skipped because it requires negating two other patterns,
  and writing this out manually would be redundant. Is there a better way?
- `f_17_agentless_passives`: DependencyMatcher doesn't let you match on there
  *not* being a certain dependency, so I can't match based on there being no
  token that is the `agent` for `by`. Instead I match all passives in one rule
  and match by-passives in the other, leaving agentless as the difference.
- `f_19_be_main_verb`: Instead of matching on "be" that is not an auxiliary, I
  matched on "be" that is the ROOT. Is that wrong?
- `f_23_wh_clause`: Need some more examples to understand what rule to write. I
  can do it with DependencyMatcher, but what dependency to look for? Dative
  comes up in the one example, but is that the right thing to match?
- For `f_25_present_participle` and `f_26_past_participle`, pseudobibeR requires
  the verb to start the sentence. But is that necessary? Consider "Joe ran out
  the door, stuffing his mouth with cookies." Is it instead sufficient just to
  get VBG/VBNs with advcl or ccomp relation?
  - It at least has the start the clause; see `f_26_past_participle` for
    counterexample when it doesn't start the sentence or clause.
- `f_35_because`: pseudobibeR forbids following "of". Necessary? Need test
  cases/examples.


Differences from pybiber:

- `f_15_gerunds`: pybiber only allows nsub, dobj, pobj, resulting in it finding
  far fewer gerunds. Not confident in what the right definition is.
- `f_42_adverbs`: pybiber does not count RBS (adverb, superlative); we do
- `f_33_pied_piping`: pybiber and pseudobiber only look for the forms "in who",
  "in whom", "in whose", and "in which"; and not, for instance, "on which" or
  "to which", though those can be pied piping too.
- `f_27_past_participle_whiz` and `f_28_present_participle_whiz`: pybiber only
  allows nouns, not proper nouns, to have the postnominal clause; we allow
  proper nouns as well. pybiber relies on the verb being immediately after the
  noun, but `DependencyMatcher` allows more complex construction (see examples).
- `f_18_by_passives`: in a parallel construction ("This was done by Steve rather
  than by Sharon"), the `DependencyMatcher` will count two by-passives, not one.

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

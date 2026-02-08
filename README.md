# matcherator: spaCy pattern-matching libraries

## pseudobiber

Rules like Biber's.

TODO notes:

- `f_15_gerunds`: pseudobibeR has a complicated strategy based on matching
  suffixes (for "ing" and "ings"). Instead I've looked for VBG (gerund or
  participle) and used the dependency relation to determine if it's acting
  noun-ally. Is that wrong?
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

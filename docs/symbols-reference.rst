Matcher rules
^^^^^^^^^^^^^

Matcher rules use spaCy's `Matcher <https://spacy.io/api/matcher>`_ class, which
pattern-matches on sequences of token attributes.

:exclamation_marks:
   Exclamation marks


   * I hate it!

:question_marks:
   Question marks


   * What do you think?

:semicolons:
   Semicolons


   * I like semicolons; they can be very useful.

:colons:
   Colons


   * She proposed a radical solution: count all the colons.

:emoji:
   Emoji


   * 💩
   * 🧠 Cognitive Dissonance Pattern

:em_dashes_unicode:
   Em dashes (Unicode)


   * This isn't about technology—it's about trust.
   * If we disagree on that, then yes — we’re speaking different languages.

:em_dashes_ascii:
   Em dashes (ASCII)


   * This isn't about technology--it's about trust.
   * This isn't about technology---it's about trust.
   * If we disagree on that, then yes -- we’re speaking different languages.

:cardinal_number:
   Cardinal numbers


   * I have three cats.
   * The cats live in unit 311.

   Counterexamples:

   * One must do one's best.
:url:
   URLs


   * You can find my website at www.example.com
   * I got it from https://www.example.com.

:email:
   Email addresses


   * Send me a message at example@example.com.
   * I got this weird message from weird@example.com and I don't know what it means.


DependencyMatcher rules
^^^^^^^^^^^^^^^^^^^^^^^

DependencyMatcher rules use spaCy's `DependencyMatcher
<https://spacy.io/api/dependencymatcher>`_ class, which pattern-matches on
structures in the dependency trees.


PhraseMatcher rules
^^^^^^^^^^^^^^^^^^^

PhraseMatcher rules use spaCy's `PhraseMatcher
<https://spacy.io/api/phrasematcher>`_ class, which matches exact words or
phrases.


Derived features
^^^^^^^^^^^^^^^^

Derived features can't be calculated from a single pattern-matching rule
directly, but are calculated from the results of several.



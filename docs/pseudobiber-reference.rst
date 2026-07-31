Matcher rules
^^^^^^^^^^^^^

Matcher rules use spaCy's `Matcher <https://spacy.io/api/matcher>`_ class, which
pattern-matches on sequences of token attributes.

:f_01_past_tense:
   Verbs in the past tense


   * The cat walked slowly down the street.

:f_02_perfect_aspect:
   Words in the perfect aspect, indicated by *have* as an auxiliary verb


   * I have written this sentence.
   * Have you been on a student exchange?
   * She has already seen it.
   * He has been told before.
   * Is this the last novel you've read?

:f_03_present_tense:
   Verbs in the present tense


   * The quick brown fox jumps over the lazy dog.

:f_04_place_adverbials:
   Place adverbials (e.g., *above*, *beside*, *outdoors*)

   TODO 'She flew west at high speed' seems like a place adverbial, but 'west' is tagged NOUN with advmod dep. Should it count?

   * Far downstream, you can find the delta.
   * I haven't found any good restaurants locally.

:f_05_time_adverbials:
   Time adverbials (e.g., *early*, *instantly*, *soon*)


   * I will leave momentarily.
   * Previously, we saw an example.
   * Moreover, music engages multiple neural systems simultaneously—including those mediating perception, cognition, memory and emotion—thereby enabling investigation of how pathological disruption of distributed neural networks manifests in alterations of affective behaviour.

:f_06_first_person_pronouns:
   First-person pronouns


   * We are very confused.
   * I bought it for myself.
   * Our examples are too simplistic.
   * My cup runneth over.

:f_07_second_person_pronouns:
   Second-person pronouns


   * You are reading this example.
   * I noticed that thy pants are on fire.
   * Take control of thyself.
   * Your simian countenance suggests a heritage unusually rich in species diversity.

:f_08_third_person_pronouns:
   Third-person pronouns


   * Their pants are collectively on fire.
   * He is a liar.
   * When I asked her, she disagreed.

:f_09_pronoun_it:
   Pronoun *it*, *its*, or *itself*


   * Its size is astounding.
   * It destroyed itself during the attempt.

:f_10_demonstrative_pronoun:
   Demonstrative pronouns, i.e., pronouns being used to replace a noun


   * That is an example sentence.

:f_11_indefinite_pronouns:
   Indefinite pronouns (e.g., *anybody*, *nothing*, *someone*)


   * Well, someone has to do it.
   * Nobody is ever interested in this topic.
   * The project went nowhere.
   * Everyone likes this example.
   * Something's not right.

:f_12_proverb_do:
   Pro-verb *do*


   * The cat did it.
   * I did it.

   Counterexamples:

   * I do not know.
:f_13_wh_question:
   Direct *wh-* questions

   TODO Need examples for the first rule, where the WH- word is after one token; then determine if that should also apply to the second rule, for clause-initial WH-questions; also, should this be restricted to questions and exclude the second example?

   * When are you leaving?
   * The difference between heights constitutes the gap, which can be measured with a depth micrometer.
   * What's happening?
   * Why don't we call the game off?

   Counterexamples:

   * I know when you are leaving.
:f_14_nominalizations:
   Nominalizations (nouns ending in *-tion*, *-ment*, *-ness*, *-ity*, e.g., *adjustment*, *abandonment*)


   * The adjustment was necessary.

   Counterexamples:

   * I went to the station.
:f_15_gerunds:
   Gerunds (participial forms functioning as nouns)

   TODO If David agrees in browndw/pybiber#7, replace with DependencyMatcher rule that checks if it is a dobj/pobj or, crucially, chains up/down to one

   * Running is fun.
   * Rather than seeking to eliminate all possibility of human error, organizations try to reduce it.
   * Future research should therefore adopt a more integrative approach that combines computational modeling of prediction errors with individual difference measures and clinical outcomes.
   * This approach focuses on reducing the likelihood of errors.

   Counterexamples:

   * I am running.
   * According to Steve, it's nice out.
   * I bought something.
:f_19_be_main_verb:
   *be* as main verb of a clause


   * I am happy.
   * Additionally, the human performance approach acknowledges that communication, both formal and informal, is essential to maintaining an effective safety culture.
   * Workers, being closest to the actual work processes, often possess valuable insights into where error precursors exist and where system vulnerabilities are most likely to manifest.
   * She's irreplaceable.
   * It was nice to just be at home.
   * It's not long.

   Counterexamples:

   * I am running.
   * If it proves to be desirable, we can upgrade the system.
:f_20_existential_there:
   Existential *there*


   * There is a feature in this sentence.
   * We see that there exist four variables.
   * There are students.
   * There is now a scholarship scheme.

:f_24_infinitives:
   Infinitives


   * I want to believe.
   * To be involved is unwise.

:f_25_present_participle:
   Present participial adverbial clauses

   Syntactically detached clauses only, to match Biber's definition

   * Stuffing his mouth with cookies, Joe ran out the door.
   * Joe ran out the door, stuffing his mouth with cookies.
   * Realizing they were completely lost, the hikers finally stopped to check their compass.
   * Hoping to avoid the rush hour traffic, we left the city long before dawn.
   * Turning the blind corner, the cyclist suddenly collided with a pedestrian.
   * The ancient water pipes finally burst during the sudden freeze, flooding the entire basement in a matter of minutes.
   * The exhausted marathon runner collapsed just past the finish line, gasping for air and clutching his side.
   * Practicing for just twenty minutes a day, you can master the basic chords on a guitar within a single month.

:f_26_past_participle:
   Past participial adverbial clauses

   Syntacticaly detached clauses only, to match Biber's definition

   * Built in a single week, the house would stand for fifty years.
   * Stored in a cool, dry place, these heirloom seeds can remain viable for up to five years.
   * The suspect finally confessed to the embezzlement scheme, cornered by the undeniable forensic evidence.

   Counterexamples:

   * After the bridge has been been built in a single week, it will fall down.
:f_34_sentence_relatives:
   Sentence relatives

   Relative clauses that refer to the predicate of a clause or to a whole clause or sentence, rather than just to a noun phrase. Detected heuristically by *which* after punctuation. TODO Is there a better DependencyMatcher rule that would work?

   * Bob likes fried mangoes, which is the most disgusting thing I've ever heard of.
   * Bob likes fried mangoes---which is the most disgusting thing I've ever heard of.
   * None of our variables have a VIF of greater than 2.5, which means that we do not need to be concerned about multicollinearity.
   * He walks for an hour each morning, which would bore me.

:f_39_prepositions:
   Total prepositional phrases



:f_40_adj_attr:
   Attributive adjectives

   Adjectives that modify a noun simply by preceding it.

   * The big horse is here.
   * I have a terrible idea!
   * It's a quick and easy fix.
   * I didn't sleep at all last night.

   Counterexamples:

   * The horse is big.
   * That's right.
   * It must be terrible.
:f_41_adj_pred:
   Predicative adjectives

   Adjectives that are linked to a noun clause with a copula (*is*).

   * The horse is big.
   * That's right.
   * It must be terrible.

   Counterexamples:

   * The big horse is here.
   * I have a terrible idea!
   * It's a quick and easy fix.
   * I didn't sleep at all last night.
:f_42_adverbs:
   Total adverbs


   * Unfortunately, that's the case.

:f_45_conjuncts:
   Conjuncts

   Connective phrases that mark relations between clauses, such as *altogether*, *in comparison*, *nonetheless*. There is also a PhraseMatcher rule to detect the remaining patterns.

   * It's a whole different kind of flying, altogether.
   * Rather than treating workers as passive recipients of safety procedures, this approach encourages workers to actively participate in identifying error-prone conditions, contributing to hazard analysis, and providing feedback on the effectiveness of existing controls and procedures.

:f_49_emphatics:
   Emphatics


   * The horse is so big.
   * He did do it.
   * It's a real big problem.

:f_50_discourse_particles:
   Discourse particles

   TODO Switch to anything with RP POS, like MFTE?

   * Well, that's not a good idea.
   * Anyway, I started blasting.
   * She tried it, but, well, it didn't work.

   Counterexamples:

   * He dug a well.
:f_51_demonstratives:
   Demonstratives (*that*, *this*, *these*, or *those* used as determiners)

   Excludes demonstrative pronouns (f_10_demonstrative_pronoun)

   * That sentence illustrates the feature.
   * This cat is happy.

   Counterexamples:

   * That is an example sentence.
   * This is the feature.
   * Those are my penguins.
:f_52_modal_possibility:
   Possibility modals


   * You can do it!
   * The bridge might fall down.

   Counterexamples:

   * Stand in awe of my might.
:f_53_modal_necessity:
   Necessity modals


   * You should wright more examples.
   * One must write examples.

   Counterexamples:

   * It smells very musty in here.
:f_54_modal_predictive:
   Predictive modals


   * You will read this example.
   * It shall be done.

   Counterexamples:

   * He wrote a will.
:f_55_verb_public:
   Public verbs


   * He announced his opinions.
   * She remarked that this example is stupid.
   * I do solemly swear that this is an example.

   Counterexamples:

   * This is a swear word.
   * He placed a bet.
:f_56_verb_private:
   Private verbs


   * I anticipate a raise.
   * I did not realise the issue.
   * She thinks it's an issue.

:f_57_verb_suasive:
   Suasive verbs


   * She decreed that none will survive.
   * I will ensure that you succeed.
   * They urged us to accept the proposal urgently.

   Counterexamples:

   * We followed the rules.
   * She read the decree.
:f_58_verb_seem:
   Verbs *seem* and *appear*


   * It seems to be the case.
   * It appears to be the case.
   * It just appeared in front of me!
   * While they were appearing, one went missing.

:f_59_contractions:
   Contractions


   * I can't do it.
   * They won't do it.
   * You shouldn't be involved.
   * They'll do it.
   * You could've done it.
   * It's a good idea.
   * She's a great teacher.
   * They're going to do it.
   * I can’t do it.
   * They won’t do it.
   * You shouldn’t be involved.
   * They’ll do it.
   * It’s a good idea.
   * She’s a great teacher.
   * They’re going to do it.

   Counterexamples:

   * The truck's fender was damaged.
   * Bob's truck was damaged.
   * The truck’s fender was damaged.
   * Bob’s truck was damaged.
:f_61_stranded_preposition:
   Prepositions stranded at the end of a sentence or clause


   * She is the candidate that I was thinking of.
   * She is the candidate that I was thinking of, before the meeting.
   * She is the candidate that I was thinking of---before the meeting.
   * I don't know who she laughed at.

   Counterexamples:

   * Let's meet face-to-face.
:f_64_phrasal_coordination:
   Phrases joined with coordinating conjunctions


   * I want ducks and drakes.
   * Swans are white and angry.
   * The cat likes to run and jump.
   * The cat struck silently and swiftly.

   Counterexamples:

   * She wrote the example, and then she tested it.
   * I came and I saw.
:f_65_clausal_coordination:
   Independent clause coordination with *and*


   * She wrote the example, and then she tested it.
   * I came and I saw.

   Counterexamples:

   * I want ducks and drakes.
:f_66_neg_synthetic:
   Synthetic negation (using *no*, *neither*, or *nor*)


   * No answer is good enough for Jones.
   * No better answer is available.
   * Neither answer is satisfactory.

:f_67_neg_analytic:
   Analytic negation (using *not* or contractions thereof)


   * That is not good enough.
   * That isn't good enough.


DependencyMatcher rules
^^^^^^^^^^^^^^^^^^^^^^^

DependencyMatcher rules use spaCy's `DependencyMatcher
<https://spacy.io/api/dependencymatcher>`_ class, which pattern-matches on
structures in the dependency trees.

:f_18_by_passives:
   *by-* passives

   Passive voice with *by* to indicate the actor

   * The task was done by Steve.
   * The task was done by Steve rather than by Sharon.

   Counterexamples:

   * The task was done.
   * By beginning this sentence with "by", I may break the feature detector.
:f_21_that_verb_comp:
   *that* verb complements


   * I said that he went.
   * This finding suggests that the item may be green.
   * We see that the data is unimodal.

:f_22_that_adj_comp:
   *that* adjective complements


   * I'm glad that you like it.
   * The values were so small that they did not have much of an effect on our model.
   * I'm sorry that you're sick.

   Counterexamples:

   * It is plausible that aberrant prediction error processing could result in sustained relief.
:f_23_wh_clause:
   *wh-* clauses


   * I believed what he told me.
   * We had a discussion about how the agency operates.
   * They investigated which chemical was responsible.
   * I believed in what he told me.
   * I believed a little of what he told me.

:f_27_past_participle_whiz:
   Past participial postnominal (reduced relative) clauses


   * The solution produced by this process is effective.
   * Steve, considered here, is a serious man.
   * Sharon's knowledge of grammar, combined with years of experience diagramming sentences, helped her write a past participle.

:f_28_present_participle_whiz:
   Present participial postnominal (reduced relative) clauses


   * The financial crisis was the event causing this decline.
   * She was the Karen causing this decline.

:f_29_that_subj:
   *that* relative clauses on subject position


   * The dog that bit me was big.
   * The Marine that bit me was big.
   * The graphs that are presented above allow us to understand the relationship.

   Counterexamples:

   * The dog that I saw was big.
   * The Marine that I saw was big.
   * The number of shares that an article gets is related to which day of the week it is published.
:f_30_that_obj:
   *that* relative clauses on object position


   * The dog that I saw was big.
   * The Marine that I saw was big.
   * The number of shares that an article gets is related to which day of the week it is published.

   Counterexamples:

   * The dog that bit me was big.
   * The Marine that bit me was big.
   * The graphs that are presented above allow us to understand the relationship.
:f_31_wh_subj:
   *wh-* relatives on subject position


   * The man who likes popcorn ate sixteen tons.
   * Our goal is to be a resource center with a reading library of materials and directors who are competent professionals.
   * Previous biomechanical analyses of pregnant women have used BSPs derived from non-pregnant populations, which may not accurately represent the substantial morphological changes that occur during pregnancy.
   * Iron and copper, which are invariably present within the apoplast in association with various metalloproteins and enzyme systems, can catalyse the oxidation of ascorbate through Fenton-type reactions, thereby accelerating the formation of monodehydroascorbate and subsequently DHA.

   Counterexamples:

   * The man who Sally likes is here.
   * Tom asked the man who went to the store.
   * The dog that saw me was big.
:f_32_wh_obj:
   *wh-* relatives on object position


   * The man who Sally likes is here.
   * I resent the man who Sally likes.
   * The goals which we indicated for phase 1 are now complete.

   Counterexamples:

   * The man who likes popcorn ate sixteen tons.
   * The detective asked the witness whom he saw at the scene.
   * To test these hypotheses, we employed a double-blind, sham-controlled experimental design wherein participants completed a battery of cognitive tasks both before and after receiving either tDCS or sham stimulation at two different current intensities.
   * The dog that I saw was big.
:f_33_pied_piping:
   Pied-piping relative clauses


   * She resented the manner in which she was told.
   * We felt that we needed a financial base on which to work.
   * He is a linguist articles by whom the editors always reject.
   * The executive to whom I addressed the complaint has recently resigned.
   * The crumbling stone bridge under which the river flows is scheduled for demolition.
   * The ancient artifact, the exact origins of which remain a subject of fierce debate among historians, is kept in a climate-controlled vault.
   * This is the report, to the findings of which they referred.

   Counterexamples:

   * She resented the manner she was told in.
   * We felt that we needed a financial base to work on.
   * Which manner was she told in?
:f_35_because:
   Causative adverbial subordinator (*because*)


   * I ate because I was hungry.
   * Because I was hungry, I ate.

   Counterexamples:

   * Because of the rain, the game was canceled.
:f_36_though:
   Concessive adverbial subordinators (*although*, *though*)


   * Although it rained, we played.
   * It was a good game, though it was rainy.

:f_37_if:
   Conditional adverbial subordinators (*if*, *unless*)


   * If it rains, we stay inside.

:f_38_other_adv_sub:
   Other adverbial subordinators (*since*, *while*, *whereas*)


   * Since it rained, we stayed inside.
   * The approach emphasizes creating redundancies, implementing cross-checks, and establishing feedback mechanisms that can catch errors before they propagate into accidents or serious incidents.
   * Developing standardised protocols for information gathering at incident scenes may also help to ensure that relevant information is systematically recorded whilst it remains readily accessible.

   Counterexamples:

   * It's been raining since noon.
   * I ate because I was hungry.
   * Because I was hungry, I ate.
   * If it rains, we stay inside.
   * Although it rained, we played.
   * It was a good game, though it was rainy.
   * Furthermore, whilst the cognitive avoidance hypothesis represents a plausible mechanistic explanation, alternative accounts merit consideration.
:f_62_split_infinitive:
   Split infinitives

   Biber's definition is *to* + ADV + (ADV) + VB, allowing only one or two intervening adverbs. We use the dependency structure to allow any number of intervening words.

   * He wants to definitively show the result.
   * I aim to boldly go where no man has gone before.
   * I aim to boldly and rapidly go where no man has gone before.

   Counterexamples:

   * He wants to show the result.
:f_63_split_auxiliary:
   Split auxiliaries

   Biber's definition is AUX + ADV + (ADV) + VB, allowing only one or two intervening adverbs. We use the dependency structure to allow any number of intervening words.

   * They are objectively shown to be split.
   * They are objectively and readily shown to be split.
   * I have already written the example.
   * The result cannot always be anticipated.
   * I would actually drive.
   * I can't ever imagine arguing with Jill.
   * They have not yet developed cancer.

   Counterexamples:

   * They are shown to be split.

PhraseMatcher rules
^^^^^^^^^^^^^^^^^^^

PhraseMatcher rules use spaCy's `PhraseMatcher
<https://spacy.io/api/phrasematcher>`_ class, which matches exact words or
phrases.

:f_45_conjuncts:
   Conjuncts

   There is also a Matcher rule for *else*, *altogether*, and *rather* following punctuation

   * I need an example of a conjunct, e.g., one like this.
   * However, it didn't work.

:f_46_downtoners:
   Downtoners


   * Are you working hard or hardly working?
   * It was somewhat difficult.
   * I was mildly annoyed.

:f_47_hedges:
   Hedges


   * Maybe I should write more examples.
   * It was kind of gross.
   * At about seven feet, she was unusually tall.

:f_48_amplifiers:
   Amplifiers


   * She came on too strongly.
   * Yeah, absolutely!
   * It's definitely an example.

:f_49_emphatics:
   Emphatics


   * I just want a puppy.
   * It's such a disappointment.


Derived features
^^^^^^^^^^^^^^^^

Derived features can't be calculated from a single pattern-matching rule
directly, but are calculated from the results of several.

:f_16_other_nouns:
   Other nouns (not counting gerunds and nominalizations)


   * There is a cat.

   Counterexamples:

   * The adjustment was necessary.
   * Running is good.
:f_17_agentless_passives:
   Agentless passive voice

   Passive voice without *by* to indicate the actor

   * The task was done.

   Counterexamples:

   * The task was done by Steve.
:f_60_that_deletion:
   Subordinator *that* deletion


   * I think he went.
   * She denies a problem occurred.
   * He alleges a small problem occurred.
   * The reporter reported the election was over.
   * He admitted he had made a catastrophic mistake.

   Counterexamples:

   * I think that he went.
   * She denies that a problem occurred.
   * He alleges that a small problem occurred.
   * The rationale helps ensure that workers understand what they should do.
   * He admitted that he had made a catastrophic mistake.


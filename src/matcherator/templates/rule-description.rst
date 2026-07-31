Matcher rules
^^^^^^^^^^^^^

Matcher rules use spaCy's `Matcher <https://spacy.io/api/matcher>`_ class, which
pattern-matches on sequences of token attributes.

{% for rule in matcher_rules %}
:{{ rule.name }}:
   {{ rule.description }}

   {% if rule.comment %}
   {{ rule.comment }}
   {% endif %}

   {% if rule.examples %}
   {% for example in rule.examples %}
   * {{ example }}
   {% endfor %}
   {% endif %}

   {% if rule.counterexamples%}
   Counterexamples:

   {% for example in rule.counterexamples %}
   * {{ example }}
   {% endfor %}
   {% endif %}
{% endfor %}

DependencyMatcher rules
^^^^^^^^^^^^^^^^^^^^^^^

DependencyMatcher rules use spaCy's `DependencyMatcher
<https://spacy.io/api/dependencymatcher>`_ class, which pattern-matches on
structures in the dependency trees.

{% for rule in dep_matcher_rules %}
:{{ rule.name }}:
   {{ rule.description }}

   {% if rule.comment %}
   {{ rule.comment }}
   {% endif %}

   {% if rule.examples %}
   {% for example in rule.examples %}
   * {{ example }}
   {% endfor %}
   {% endif %}

   {% if rule.counterexamples%}
   Counterexamples:

   {% for example in rule.counterexamples %}
   * {{ example }}
   {% endfor %}
   {% endif %}
{% endfor %}

PhraseMatcher rules
^^^^^^^^^^^^^^^^^^^

PhraseMatcher rules use spaCy's `PhraseMatcher
<https://spacy.io/api/phrasematcher>`_ class, which matches exact words or
phrases.

{% for rule in phrase_matcher_rules %}
:{{ rule.name }}:
   {{ rule.description }}

   {% if rule.comment %}
   {{ rule.comment }}
   {% endif %}

   {% if rule.examples %}
   {% for example in rule.examples %}
   * {{ example }}
   {% endfor %}
   {% endif %}

   {% if rule.counterexamples%}
   Counterexamples:

   {% for example in rule.counterexamples %}
   * {{ example }}
   {% endfor %}
   {% endif %}
{% endfor %}

Derived features
^^^^^^^^^^^^^^^^

Derived features can't be calculated from a single pattern-matching rule
directly, but are calculated from the results of several.

{% for rule in derived_rules %}
:{{ rule.name }}:
   {{ rule.description }}

   {% if rule.comment %}
   {{ rule.comment }}
   {% endif %}

   {% if rule.examples %}
   {% for example in rule.examples %}
   * {{ example }}
   {% endfor %}
   {% endif %}

   {% if rule.counterexamples%}
   Counterexamples:

   {% for example in rule.counterexamples %}
   * {{ example }}
   {% endfor %}
   {% endif %}
{% endfor %}

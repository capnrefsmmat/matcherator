{% macro examples(rule) %}
   {% if rule.examples %}
   {% for example in rule.examples %}
   * {{ example | indent(5) }}
   {% endfor %}
   {% endif %}

   {% if rule.counterexamples %}
   Counterexamples:

   {% for example in rule.counterexamples %}
   * {{ example | indent(5) }}
   {% endfor %}
   {% endif %}
{% endmacro %}
{% for rule in features %}
:{{ rule.name }}:
   {{ rule.description | indent(3) }}

   {% if rule.comment %}
   {{ rule.comment | indent(3) }}
   {% endif %}

{{ examples(rule) }}
{% endfor %}

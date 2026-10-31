"""Generate a reST document listing all rules in a set."""

from jinja2 import Environment, PackageLoader, select_autoescape

import argparse
import json
import importlib.resources

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate reST reference documentation of rules.")
    parser.add_argument("ruleset", help="Name of ruleset to generate (e.g., pseudobiber.json)")

    args = parser.parse_args()

    rule_text = importlib.resources.files("matcherator.rules") \
                                   .joinpath(args.ruleset) \
                                   .read_text()

    rules = json.loads(rule_text)

    env = Environment(
        loader=PackageLoader("matcherator"),
        autoescape=select_autoescape(),
        trim_blocks=True, lstrip_blocks=True
    )

    template = env.get_template("rule-description.rst")

    variables = {
        "ruleset_name": args.ruleset,
        "features": [{"name": name,
                      "description": r.get("description", ""),
                      "comment": r.get("comment", ""),
                      "examples": r.get("examples", []),
                      "counterexamples": r.get("counterexamples", [])}
                     for name, r in rules.items()]
    }
    print(template.render(variables))

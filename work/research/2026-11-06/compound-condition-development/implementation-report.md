Implemented the development contract in three new files:

- [condition_expression.py](/home/mjbommar/projects/personal/moratorium-data-2026/scripts/condition_expression.py)
- [test_condition_expression.py](/home/mjbommar/projects/personal/moratorium-data-2026/tests/test_condition_expression.py)
- [1.0.0.json](/home/mjbommar/projects/personal/moratorium-data-2026/work/schemas/condition-expression/1.0.0.json)

The recursive transport preserves clause context and quotations, nested group semantics, and explicit text or unknown expressions for unresolved conditions. Groups are limited to **128 members** so standard JSON Schema can enforce the same cardinality constraint as Pydantic.

Validation passed: five tests using `/home/mjbommar/projects/bc/bc-modules/.venv/bin/python`, covering semantic distinctions, nesting, invalid inputs, and schema equivalence. No paid APIs were called and no commit was made.

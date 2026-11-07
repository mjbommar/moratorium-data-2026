"""Strict complete-clause comparison for frozen extraction development slots.

This compares reviewed structured expectations, not textual entailment or legal
truth. Commutative group members may change order; operators, cardinality,
clause roles, contexts, all threshold fields and textual predicates may not.
"""
import json


def semantic_key(value):
    if isinstance(value, list):
        return sorted((semantic_key(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, dict):
        return {key: semantic_key(item) for key, item in sorted(value.items())
                if key != 'source_text' or 'purpose' not in value}
    return value


def matches_condition_clauses(actual, expected):
    from condition_expression import validate_condition_clauses
    if validate_condition_clauses(actual) or validate_condition_clauses(expected):
        return False
    return semantic_key(actual) == semantic_key(expected)

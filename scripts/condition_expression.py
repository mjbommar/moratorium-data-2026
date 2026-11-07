"""Development transport for source-qualified condition expressions.

Group size is bounded so the generated standard JSON Schema can express the
same count-versus-members constraint without nonstandard $data extensions.
Source quotations are retained verbatim; their accuracy is a review question.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, TypeAdapter, field_validator, model_validator

MAX_MEMBERS = 128
SCHEMA_ID = 'https://moratorium-data.org/schemas/condition-expression/1.0.0.json'
Nonempty = Annotated[str, Field(min_length=1, strict=True)]


class Transport(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class Threshold(Transport):
    type: Literal['threshold']
    operator: Literal['lt', 'le', 'eq', 'ge', 'gt', 'unknown']
    value: StrictInt | StrictFloat | None
    unit: Nonempty | None
    measurement_basis: Nonempty | None
    aggregation_rule: Nonempty | None
    scope: Nonempty | None


class TextPredicate(Transport):
    type: Literal['text_predicate']
    text: Nonempty


class Unknown(Transport):
    type: Literal['unknown']
    source_text: Nonempty


def _member_schema(schema: dict) -> None:
    schema['uniqueItems'] = True


class All(Transport):
    type: Literal['all']
    members: Annotated[list['Expression'], Field(min_length=1, max_length=MAX_MEMBERS, strict=True)]

    @model_validator(mode='after')
    def distinct_members(self):
        _check_distinct(self.members)
        return self


class Any(Transport):
    type: Literal['any']
    members: Annotated[list['Expression'], Field(min_length=1, max_length=MAX_MEMBERS, strict=True)]

    @model_validator(mode='after')
    def distinct_members(self):
        _check_distinct(self.members)
        return self


def _at_least_schema(schema: dict) -> None:
    # A finite set of implications encodes count <= len(members) in draft 2020-12.
    schema['allOf'] = [
        {'if': {'properties': {'count': {'const': n}}, 'required': ['count']},
         'then': {'properties': {'members': {'minItems': n}}}}
        for n in range(2, MAX_MEMBERS + 1)
    ]


class AtLeast(Transport):
    type: Literal['at_least']
    count: Annotated[StrictInt, Field(ge=1, le=MAX_MEMBERS)]
    members: Annotated[list['Expression'], Field(min_length=1, max_length=MAX_MEMBERS, strict=True)]

    @field_validator('count', mode='before')
    @classmethod
    def json_integer(cls, value):
        # JSON Schema integer includes integral JSON number values such as 2.0.
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    @model_validator(mode='after')
    def valid_members(self):
        _check_distinct(self.members)
        if self.count > len(self.members):
            raise ValueError('count cannot exceed the number of members')
        return self


def _check_distinct(members: list) -> None:
    # Pydantic model equality is structural and treats JSON numbers 1 and 1.0
    # as equal, matching JSON Schema's uniqueItems semantics.
    if any(member == other for i, member in enumerate(members) for other in members[:i]):
        raise ValueError('members must not contain identical children')


Expression = Annotated[Union[Threshold, TextPredicate, Unknown, All, Any, AtLeast], Field(discriminator='type')]
for _model in (All, Any, AtLeast):
    _model.model_rebuild()


class ConditionClause(Transport):
    purpose: Literal['definition', 'prohibition_trigger', 'procedure_trigger', 'safe_harbor', 'exemption', 'other', 'unknown']
    assertion_context: Literal['proposed', 'source_reported', 'enacted_text', 'unknown']
    source_text: Nonempty
    expression: Expression


# Native output transports preserve structurally parseable candidates even when
# a group's semantic constraints fail. Validate each value with the full contract
# after extraction, retaining valid neighboring facts and error flags.
class NativeAll(Transport):
    type: Literal['all']
    members: list['NativeExpression']


class NativeAny(Transport):
    type: Literal['any']
    members: list['NativeExpression']


class NativeAtLeast(Transport):
    type: Literal['at_least']
    count: StrictInt
    members: list['NativeExpression']


NativeExpression = Annotated[Union[Threshold, TextPredicate, Unknown, NativeAll, NativeAny, NativeAtLeast], Field(discriminator='type')]
for _model in (NativeAll, NativeAny, NativeAtLeast):
    _model.model_rebuild()


class NativeConditionClause(Transport):
    purpose: Literal['definition', 'prohibition_trigger', 'procedure_trigger', 'safe_harbor', 'exemption', 'other', 'unknown']
    assertion_context: Literal['proposed', 'source_reported', 'enacted_text', 'unknown']
    source_text: Nonempty
    expression: NativeExpression


_CLAUSES = TypeAdapter(Annotated[list[ConditionClause], Field(strict=True)])


def validate_condition_clauses(value) -> list[str]:
    """Return validation errors, or an empty list for valid clause data."""
    from pydantic import ValidationError
    try:
        _CLAUSES.validate_python(value)
    except ValidationError as exc:
        return [f"{'.'.join(map(str, error['loc'])) or '<root>'}: {error['msg']}" for error in exc.errors()]
    return []


def condition_clauses_schema() -> dict:
    """Return the self-contained schema for the helper's list input."""
    schema = _CLAUSES.json_schema()
    # Native model-output schemas omit unsupported uniqueItems/if/then/allOf.
    # Canonical JSON Schema and Python validators independently enforce these.
    for name in ('All','Any','AtLeast'):
        schema['$defs'][name]['properties']['members']['uniqueItems'] = True
    _at_least_schema(schema['$defs']['AtLeast'])
    schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    schema['$id'] = SCHEMA_ID
    return schema


if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'work/schemas/condition-expression/1.0.0.json'
    path.write_text(json.dumps(condition_clauses_schema(), indent=2, ensure_ascii=False) + '\n')

"""Typed electoral/legal candidates over the real bc-evidence chunk pipeline.

No canonical IDs, review decisions, legal conclusions or database writes are
created here. Passing a field schema and locating a quote only nominates a fact
for review; neither verifies that the quoted passage entails the model's value.
"""
import hashlib
import json
import fcntl
from pathlib import Path
from typing import Literal, Annotated, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictFloat, StrictStr, create_model
from jsonschema import Draft202012Validator, FormatChecker
from bc_evidence.extract import ExtractedClaim, ChunkExtraction

import extract_document_resumable as resumable

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'work/schemas/expanded/1.0.0.json'


class CandidateObject(BaseModel):
    model_config = ConfigDict(extra='forbid')


class DateBounds(CandidateObject):
    earliest: str | None
    latest: str | None
    precision: Literal['day', 'month', 'year', 'range', 'unknown']
    original_text: str | None


class CalendarDuration(CandidateObject):
    value: StrictInt | None
    unit: Literal['days', 'calendar_months', 'calendar_years', 'unknown']
    anchor: Literal['adoption', 'enactment', 'effective_date', 'applicability_date', 'specified_date', 'unknown']
    anchor_date: DateBounds | None
    original_text: str


class Threshold(CandidateObject):
    operator: Literal['lt', 'le', 'eq', 'ge', 'gt', 'unknown']
    value: StrictInt | StrictFloat | None
    unit: str | None
    measurement_basis: str | None
    aggregation_rule: str | None
    scope: str | None


# These are extraction targets, not a permission to write every canonical field.
# Identity, derived outcomes, supersession and review/claim references are excluded.
FIELDS = {
    'elections': {'election_date', 'administering_authority', 'election_type'},
    'ballot_measures': {'designation', 'wording', 'title', 'placement_method',
                        'placement_source_term', 'legal_basis', 'lifecycle', 'bindingness',
                        'sectors', 'yes_direction', 'referendum_yes_effect', 'scope_note'},
    'measure_provisions': {'mechanism', 'bindingness', 'covered_uses', 'thresholds',
                           'exemptions', 'geography', 'implementation_requirements', 'duration'},
    'measure_results': {'yes_votes', 'no_votes', 'blank_votes', 'ballots_cast',
                        'registered_voters', 'undervotes', 'overvotes', 'precincts_reporting',
                        'precincts_total', 'source_yes_percent', 'percentage_denominator',
                        'passage_threshold', 'threshold_comparison', 'reported_outcome',
                        'reporting_status', 'certification_status', 'certification_date'},
}


class SupportingPassage(CandidateObject):
    quote: str = Field(min_length=1, description='Additional verbatim source passage; never a paraphrase')
    role: Literal['definition', 'operative_clause', 'authority', 'exception',
                  'override', 'limitation', 'actor', 'electorate', 'territory',
                  'reporting_scope', 'other']


class FactBase(CandidateObject):
    target_table: Literal['elections', 'ballot_measures', 'measure_provisions', 'measure_results']
    subject_label: str = Field(min_length=1, description='Source-named jurisdiction, question and/or instrument; no invented ID')
    quote: str = Field(min_length=1, description='Exact source text supporting this particular field value')
    assertion_context: Literal['proposed', 'source_reported', 'enacted_text', 'unknown']
    supporting_passages: list[SupportingPassage] = Field(default_factory=list)


def _typed_facts():
    """Derive transport shapes/enums from the actual canonical field definitions.

    Identical field schemas share one branch to keep native-output schemas small.
    Full canonical constraints, table/field pairing and evidence remain independent
    post-extraction checks. No text-to-list or prose-to-enum coercions are used.
    """
    schema = json.loads(SCHEMA.read_text())
    groups = {}
    for table, fields in sorted(FIELDS.items()):
        for field in sorted(fields):
            prop = schema['$defs'][table]['properties'][field]
            key = resumable.digest(prop)
            groups.setdefault(key, {'fields': set(), 'schema': prop})['fields'].add(field)
    models = []
    for index, group in enumerate(groups.values()):
        prop = group['schema']
        if 'enum' in prop:
            annotation = Literal[tuple(prop['enum'])]
        elif prop.get('$ref') == '#/$defs/date_bounds':
            annotation = DateBounds
        elif any(p.get('$ref') == '#/$defs/calendar_duration' for p in prop.get('anyOf', [])):
            annotation = CalendarDuration | None
        else:
            kinds = prop.get('type', [])
            kinds = [kinds] if isinstance(kinds, str) else kinds
            kind = next(k for k in kinds if k != 'null')
            if kind == 'array':
                item = prop['items']
                annotation = (list[Threshold] if item.get('$ref') == '#/$defs/threshold' else
                              list[Literal[tuple(item['enum'])]] if 'enum' in item else list[StrictStr])
            else:
                annotation = {'string': StrictStr, 'integer': StrictInt,
                              'number': StrictInt | StrictFloat}[kind]
            if 'null' in kinds:
                annotation = annotation | None
        models.append(create_model(f'DomainFact{index:02d}', __base__=FactBase,
                                    target_field=(Literal[tuple(sorted(group['fields']))], ...),
                                    value=(annotation, ...)))
    return Annotated[Union[tuple(models)], Field(discriminator='target_field')]


TypedDomainFact = _typed_facts()


class DomainClaim(ExtractedClaim):
    model_config = ConfigDict(extra='forbid')
    facts: list[TypedDomainFact] = Field(default_factory=list)


class DomainChunk(ChunkExtraction):
    model_config = ConfigDict(extra='forbid')
    claims: list[DomainClaim] = Field(default_factory=list)
    unresolved_fields: list[str] = Field(default_factory=list)


INSTRUCTIONS = '''
DOMAIN CANDIDATES (unreviewed): Each claim may also have facts. For each fact name
target_table, target_field, subject_label, typed value, exact supporting quote and
assertion_context. Use only these table/field pairs:
{fields}
Preserve calendar months versus days, duration anchor, inequalities, units,
aggregate-area basis, conjunctive conditions, exemptions and conditional language.
Use supporting_passages for additional exact passages needed to support a composed
value, labeling each passage's role. A statutory citation's occurrence does not
prove affirmative authority: distinguish authority, notwithstanding/override,
exceptions and limitations in legal_basis itself. Do not flatten these roles into
an unqualified citation list. Carry defined measurement composition explicitly in
measurement_basis, including associated impervious surfaces when applicable;
quote both the operative threshold and its definition using supporting_passages.
Distinguish the requested actor, electorate and territorial reach. A city's name
in a request to that city does not establish that the township vote governs the
city's entire territory. Omit unproved geography and record it as unresolved.
Do not classify advisory_support/advisory_opposition when the reference axis is
unspecified; preserve the requested action in scope_note and bindingness separately.
Full precinct reporting alone does not establish complete ballot counting. Use
reporting_status=complete only when the source explicitly supports completion of
the contest count; otherwise preserve precinct counts and unknown reporting status.
For duration, original_text must copy the operative duration passage. Do not infer
an actual anchor_date from an unproved passage/enactment event.
Represent reported yes, no and blank counts separately. Never infer ballots_cast,
blank/undervotes, turnout or certification from the sum of yes and no, a signature,
a news report or a broader election total. Do not calculate outcomes or legal force.
Quote each field's support verbatim. Do not assign canonical IDs or claim references.
Do not invent facts for absent fields: list important missing/uncertain fields in
unresolved_fields. A proposal's clauses may be extracted as proposed while actual
bindingness, voter wording/polarity, certification and effective dates remain unknown.
'''


def field_validator(schema, table, field):
    if field not in FIELDS.get(table, set()):
        return None
    property_schema = schema['$defs'][table]['properties'][field]
    return Draft202012Validator({'$defs': schema['$defs'], **property_schema},
                                format_checker=FormatChecker())


def review_candidates(state, schema):
    """Keep invalid, ambiguous and conflicting candidates visible for review."""
    document = state['context']['document']
    text = document['text']
    candidates = {}
    unresolved = set()
    for request_hash, cached in state['successes'].items():
        # Summary-reduction outputs have no claims and create no field candidates.
        if 'claims' not in cached['output']:
            continue
        if resumable.digest(cached['output']) != cached['output_sha256']:
            raise ValueError('Domain cache output hash mismatch')
        chunk = DomainChunk.model_validate(cached['output'])
        unresolved.update(chunk.unresolved_fields)
        for claim in chunk.claims:
            for fact in claim.facts:
                raw = fact.model_dump(mode='json')
                key = resumable.digest(raw)
                if key in candidates:
                    if request_hash not in candidates[key]['request_hashes']:
                        candidates[key]['request_hashes'].append(request_hash)
                    continue
                validator = field_validator(schema, fact.target_table, fact.target_field)
                errors = (['Unsupported extraction field'] if validator is None else
                          [e.message for e in validator.iter_errors(raw['value'])])
                spans = []
                offset = 0
                while (found := text.find(fact.quote, offset)) >= 0:
                    spans.append([found, found + len(fact.quote)])
                    offset = found + 1
                flags = []
                supporting = []
                for passage in fact.supporting_passages:
                    passage_spans = []
                    start = 0
                    while (found := text.find(passage.quote, start)) >= 0:
                        passage_spans.append([found, found + len(passage.quote)])
                        start = found + 1
                    supporting.append({**passage.model_dump(mode='json'),
                                       'exact_quote_spans': passage_spans})
                    if not passage_spans:
                        flags.append('supporting_quote_unlocated')
                    elif len(passage_spans) > 1:
                        flags.append('supporting_quote_location_ambiguous')
                if errors:
                    flags.append('field_schema_invalid')
                if not spans:
                    flags.append('quote_unlocated')
                elif len(spans) > 1:
                    flags.append('quote_location_ambiguous')
                if fact.assertion_context == 'proposed':
                    flags.append('proposal_only')
                    if (fact.target_table == 'measure_results' or
                        fact.target_table == 'ballot_measures' and fact.target_field in
                            {'wording', 'yes_direction', 'referendum_yes_effect', 'bindingness', 'lifecycle'}):
                        flags.append('election_specific_evidence_required')
                # Even valid, located candidates are NEVER accepted automatically.
                candidates[key] = {**raw, 'candidate_id': key,
                                   'source_document_id': document['doc_id'],
                                   'body_sha256': document['body_sha256'],
                                   'text_sha256': document['text_sha256'],
                                   'request_hashes': [request_hash], 'exact_quote_spans': spans,
                                   'supporting_passage_locations': supporting,
                                   'field_schema_errors': errors, 'review_flags': flags,
                                   'review_status': 'unreviewed', 'accepted': False}
    by_field = {}
    for candidate in candidates.values():
        group = (candidate['target_table'], candidate['target_field'], candidate['subject_label'])
        by_field.setdefault(group, []).append(candidate)
    for group in by_field.values():
        if len({resumable.digest(c['value']) for c in group}) > 1:
            for candidate in group:
                candidate['review_flags'].append('conflicting_field_candidates')
    return {'candidates': list(candidates.values()), 'unresolved_fields': sorted(unresolved),
            'domain_review_complete': False, 'canonical_records_written': 0,
            'limitations': ['Field-schema validity does not establish textual entailment.',
                            'Located quotes do not establish legal effect or identity.',
                            'Candidate conflicts remain unresolved; no majority vote or confidence merge.']}


async def run(directory, doc, cells, *, question, **kwargs):
    if hashlib.sha256(doc['text'].encode()).hexdigest() != doc.get('text_sha256'):
        raise ValueError('Document text hash mismatch')
    body_hash = doc.get('body_sha256', '')
    if len(body_hash) != 64 or any(c not in '0123456789abcdef' for c in body_hash):
        raise ValueError('Original payload hash required')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (directory / 'domain.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            return await _run_locked(directory, doc, cells, question=question, **kwargs)
        except resumable.WorkspaceContextChanged:
            # A rejected new context must not destroy the historical run's result.
            raise
        except BaseException:
            (directory / 'domain-candidates.private.json').unlink(missing_ok=True)
            raise


async def _run_locked(directory, doc, cells, *, question, **kwargs):
    schema = json.loads(SCHEMA.read_text())
    identity = {**kwargs.pop('model_identity'),
                'domain_adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'expanded_schema_sha256': hashlib.sha256(SCHEMA.read_bytes()).hexdigest()}
    instruction = INSTRUCTIONS.format(fields=json.dumps({k: sorted(v) for k, v in FIELDS.items()}))
    result = await resumable.run(directory, doc, cells, question=question + '\n' + instruction,
                                 model_identity=identity, chunk_output_type=DomainChunk, **kwargs)
    state = json.loads((Path(directory) / 'state.private.json').read_text())
    candidates = review_candidates(state, schema)
    candidates['context_sha256'] = state['context_sha256']
    candidates['full_text_chunk_coverage'] = result['full_text_chunk_coverage']
    resumable.save(Path(directory) / 'domain-candidates.private.json', candidates)
    return candidates

#!/usr/bin/env python3
"""Export one authorized Codex rollout into contest schema 1.0.

Only public user/assistant messages and tool records are included. Original
timestamps, session ID and rollout ordinals are retained; no events are invented.
Raw files are read only and are never copied into the repository.
"""
import argparse
import collections
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


RULES = [
    (re.compile(r'\bsk-[A-Za-z0-9_-]{16,}'), '[REDACTED_API_KEY]'),
    (re.compile(r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}'), '[REDACTED_GITHUB_TOKEN]'),
    (re.compile(r'Bearer\s+[A-Za-z0-9._+/=-]{12,}', re.I), 'Bearer [REDACTED]'),
    # Huawei keys do not necessarily carry an sk- prefix. Preserve pure hex
    # hashes/UUIDs; redact long mixed-case, digit-bearing opaque strings.
    (re.compile(r'(?<![A-Za-z0-9])(?=[A-Za-z0-9_+/=-]{24,}(?![A-Za-z0-9]))(?=[A-Za-z0-9_+/=-]*[A-Z])(?=[A-Za-z0-9_+/=-]*[a-z])(?=[A-Za-z0-9_+/=-]*[0-9])[A-Za-z0-9_+/=-]{24,}'), '[REDACTED_OPAQUE_TOKEN]'),
]


def scrub(value, counts):
    if isinstance(value, str):
        for pattern,replacement in RULES:
            value,n = pattern.subn(replacement,value)
            counts[0] += n
        return value
    if isinstance(value, list):
        return [scrub(x,counts) for x in value]
    if isinstance(value, dict):
        return {k:scrub(v,counts) for k,v in value.items()}
    return value


def convert(raw):
    payload = raw.get('payload',{})
    if raw.get('type') != 'response_item':
        return None
    kind = payload.get('type')
    if kind == 'message':
        role = payload.get('role')
        if role not in ['user','assistant']:
            return None
        parts = payload.get('content',[])
        texts = [p['text'] for p in parts if p.get('type') in ['input_text','output_text','text'] and isinstance(p.get('text'),str)]
        if not texts:
            return None
        return {'role':role,'text':'\n'.join(texts)}
    if kind in ['function_call','custom_tool_call']:
        value = payload.get('arguments',payload.get('input'))
        if kind == 'function_call' and isinstance(value,str):
            try: value=json.loads(value)
            except ValueError: pass
        return {'role':'tool','tool_name':payload['name'],'tool_call_id':payload['call_id'],'input':value,'output':None}
    if kind in ['function_call_output','custom_tool_call_output']:
        return {'role':'tool','tool_name':'<result>','tool_call_id':payload['call_id'],'input':None,'output':payload.get('output')}
    if kind == 'web_search_call':
        return {'role':'tool','tool_name':'web_search','tool_call_id':payload['id'],'input':payload.get('action'),'output':None}
    return None


def export(source, repo, login, team):
    data = source.read_bytes()
    records = [json.loads(line) for line in data.splitlines() if line.strip()]
    meta = next(r['payload'] for r in records if r.get('type') == 'session_meta')
    if meta.get('cwd') != '/home/test/ai_completion':
        raise ValueError('Refusing to export a different workspace without revising the explicit allowlist.')
    sid = meta['id']
    events=[]
    excluded=collections.Counter()
    substitutions=0
    for raw in records:
        converted=convert(raw)
        if converted is None:
            excluded[f'{raw.get("type")}:{raw.get("payload",{}).get("type")}']+=1
            continue
        count=[0]
        converted=scrub(converted,count)
        substitutions+=count[0]
        event={'schema_version':'1.0','session_id':sid,'team_id':team,'github_login':login,
               'tool':'codex','seq':len(events),'ts':raw['timestamp'],**converted,
               'source_ordinal':raw.get('ordinal'),'redacted_count':count[0]}
        events.append(event)
    date=events[0]['ts'][:10]
    rel=Path('logs')/login/date/f'codex__{sid}.jsonl'
    dest=repo/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),encoding='utf-8')
    manifest={'schema_version':'1.0','team_id':team,'github_login':login,
              'generator':'codex-rollout-contest-export@1.0','updated_at':datetime.now(timezone.utc).isoformat(),
              'sessions':[{'session_id':sid,'tool':'codex','started_at':events[0]['ts'],
                           'last_event_at':events[-1]['ts'],'event_count':len(events),'file_path':str(rel),
                           'collection_mode':'cli','redacted_count_total':substitutions,'health':'degraded',
                           'data_completeness_warning':'Explicit read-only export of Codex public rollout events. System/developer instructions, reasoning, compaction context and image bytes excluded. Event payload text is otherwise retained with automated secret redaction. This is not a claim of having run the official collector plugin.'}]}
    (repo/'logs'/login/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    audit={'source_file':source.name,'source_bytes':len(data),'source_sha256':hashlib.sha256(data).hexdigest(),
           'export_file':str(rel),'export_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
           'event_count':len(events),'roles':dict(collections.Counter(e['role'] for e in events)),
           'redaction_substitutions':substitutions,'excluded_record_types':dict(excluded),
           'cutoff_timestamp':records[-1].get('timestamp'),'format':'contest schema 1.0, custom transparent converter',
           'caution':'Original local source is unmodified. Export metadata discloses exclusions; obtain organizer acceptance if raw collector format is mandated.'}
    (repo/'logs'/login/'export-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:audit[k] for k in ['export_file','event_count','roles','redaction_substitutions']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('repo',type=Path)
    p.add_argument('--login',required=True)
    p.add_argument('--team',required=True)
    a=p.parse_args()
    export(a.source,a.repo,a.login,a.team)

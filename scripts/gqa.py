#!/usr/bin/env python3
"""Deterministic guardrails for the General QA Pipeline.

Python standard library only. Python >= 3.10.

Usage:
  python scripts/gqa.py validate [path ...]   # default: all artifacts in work/ and examples/
  python scripts/gqa.py find <query terms>    # search saved QA work (work/ only)
  python scripts/gqa.py list [--open]         # list QA work with verdicts (work/ only)

Exit codes: 0 ok, 1 validation errors / bad usage.
"""

import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# validate covers synthetic examples too; find/list operate on real QA work only
VALIDATE_DIRS = ['work', 'examples']
OPERATIONAL_DIRS = ['work']

CHECK_STATUSES = ['PASS', 'FAIL', 'BLOCKED', 'NEEDS_VERIFICATION']
RETEST_STATUSES = ['FIX_VERIFIED', 'STILL_FAILING', 'BLOCKED', 'NEEDS_VERIFICATION']
VERDICTS = ['PASS', 'FAIL', 'BLOCKED', 'NEEDS_VERIFICATION']
SCOPE_STATES = ['APPLICABLE', 'N/A', 'ONLY_ON_FAILURE', 'UNAVAILABLE']
CLASSIFICATIONS = ['PRODUCT_DEFECT', 'REQUIREMENT_AMBIGUITY', 'ENVIRONMENT',
                   'TEST_DATA', 'AGENT_FALSE_POSITIVE', 'UNKNOWN']
RECOMMENDATIONS = ['READY', 'NOT_READY', 'NEEDS_VERIFICATION']

SECRET_PATTERNS = [
    (re.compile(r'bearer\s+[a-z0-9._\-]{16,}', re.I), 'possible bearer token'),
    (re.compile(r'api[_-]?key\s*[:=]\s*[^\s<*]{8,}', re.I), 'possible API key'),
    (re.compile(r'password\s*[:=]\s*[^\s<*]{4,}', re.I), 'possible password'),
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'), 'private key'),
    (re.compile(r'\bsk-[a-zA-Z0-9]{20,}'), 'possible secret key'),
    (re.compile(r'eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}'), 'possible JWT'),
    (re.compile(r'(session|auth)[_-]?token\s*[:=]\s*[^\s<*]{8,}', re.I), 'possible session token'),
]

# ---------- artifact discovery ----------

def is_qa_work(content):
    return re.search(r'^# QA Work:', content, re.M) is not None


def walk_md(directory, acc):
    if not os.path.isdir(directory):
        return acc
    for entry in sorted(os.listdir(directory)):
        p = os.path.join(directory, entry)
        if os.path.isdir(p):
            if entry == 'node_modules' or entry.startswith('.'):
                continue
            walk_md(p, acc)
        elif entry.endswith('.md'):
            acc.append(p)
    return acc


def all_artifacts(dirs):
    files = []
    for d in dirs:
        walk_md(os.path.join(ROOT, d), files)
    result = []
    for f in files:
        try:
            with open(f, encoding='utf-8') as fh:
                if is_qa_work(fh.read()):
                    result.append(f)
        except OSError:
            pass
    return result

# ---------- parsing ----------

def parse_artifact(content):
    lines = content.split('\n')
    art = {
        'title': None, 'meta': {}, 'scope': {}, 'checks': [], 'findings': [],
        'defects': [], 'retests': [], 'verdict': {}, 'id_headings': [],
        'sections': set(),
    }
    section = None
    block = None  # current ### block: {kind, id, heading, line, fields}

    def flush():
        nonlocal block
        if not block:
            return
        kind = block['kind']
        if kind == 'check':
            art['checks'].append(block)
        elif kind == 'finding':
            art['findings'].append(block)
        elif kind == 'defect':
            art['defects'].append(block)
        elif kind == 'retest':
            art['retests'].append(block)
        block = None

    for i, raw in enumerate(lines):
        line = raw.rstrip('\r')
        m = re.match(r'^# QA Work:\s*(.*)', line)
        if m:
            art['title'] = m.group(1).strip()
            continue
        m = re.match(r'^## (.+)', line)
        if m:
            flush()
            section = m.group(1).strip()
            art['sections'].add(section)
            continue
        m = re.match(r'^### (.+)', line)
        if m:
            flush()
            heading = m.group(1).strip()
            idm = re.search(r'\b(REQ|CHK|FIND|DEF)-\d{3}\b', heading)
            art_id = idm.group(0) if idm else None
            if art_id:
                art['id_headings'].append({'id': art_id, 'line': i + 1})
            kind = ('check' if section == 'Checks'
                    else 'finding' if section == 'Findings'
                    else 'defect' if section == 'Defects'
                    else 'retest' if section == 'Retest History'
                    else 'other')
            block = {'kind': kind, 'id': art_id, 'heading': heading,
                     'line': i + 1, 'fields': {}}
            continue
        m = re.match(r'^- ([A-Za-z /]+):\s*(.*)$', line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if block:
                block['fields'][key] = val
            elif section == 'Metadata':
                art['meta'][key] = val
            elif section == 'Verification Scope':
                art['scope'][key] = val
            elif section == 'Final Verdict':
                art['verdict'][key] = val
            continue
        # REQ list items: "- REQ-001: ..."
        m = re.match(r'^- (REQ-\d{3}):', line)
        if m:
            art['id_headings'].append({'id': m.group(1), 'line': i + 1})
    flush()
    return art

# ---------- validation ----------

def is_empty_val(v):
    return not v or re.match(r'^(-|none|n/a|<.*>)$', v.strip(), re.I) is not None


def validate_artifact(file):
    errors = []
    warnings = []
    with open(file, encoding='utf-8') as fh:
        content = fh.read()
    art = parse_artifact(content)
    err = errors.append
    warn = warnings.append

    if not art['title']:
        err('missing "# QA Work: <title>" heading')

    # duplicate IDs
    seen = {}
    for h in art['id_headings']:
        art_id, line = h['id'], h['line']
        if art_id in seen:
            err('duplicate ID {} (lines {} and {})'.format(art_id, seen[art_id], line))
        else:
            seen[art_id] = line
    known_ids = set(seen.keys())

    # required sections
    for s in ['Metadata', 'Source', 'Checks', 'Final Verdict']:
        if s not in art['sections']:
            err('missing required section "## {}"'.format(s))

    # verification scope states
    for layer, val in art['scope'].items():
        v = val.split('—')[0].split(' - ')[0].strip()
        if v and not v.startswith('<') and v not in SCOPE_STATES:
            err('Verification Scope {}: invalid state "{}" (allowed: {})'.format(
                layer, v, ', '.join(SCOPE_STATES)))

    # checks
    counts = {'PASS': 0, 'FAIL': 0, 'BLOCKED': 0, 'NEEDS_VERIFICATION': 0}
    for c in art['checks']:
        label = c['id'] or 'check at line {}'.format(c['line'])
        status = c['fields'].get('Status', '').strip()
        if status not in CHECK_STATUSES:
            err('{}: invalid or missing Status "{}" (allowed: {})'.format(
                label, status, ', '.join(CHECK_STATUSES)))
        else:
            counts[status] += 1
            if status in ('PASS', 'FAIL') and is_empty_val(c['fields'].get('Evidence')):
                err('{}: status {} requires non-empty Evidence'.format(label, status))
        req = c['fields'].get('Requirement', '').strip()
        if req and not is_empty_val(req):
            for r in re.split(r'[,\s]+', req):
                if re.match(r'^REQ-\d{3}$', r) and r not in known_ids:
                    err('{}: references missing {}'.format(label, r))
        if is_empty_val(c['fields'].get('Oracle')):
            warn('{}: no Oracle recorded'.format(label))

    # defects
    for d in art['defects']:
        label = d['id'] or 'defect at line {}'.format(d['line'])
        cls = d['fields'].get('Classification', '').strip()
        if cls not in CLASSIFICATIONS:
            err('{}: invalid or missing Classification "{}"'.format(label, cls))
        finds = d['fields'].get('Findings', '').strip()
        refs = [x for x in re.split(r'[,\s]+', finds) if re.match(r'^FIND-\d{3}$', x)]
        if not refs:
            err('{}: must reference at least one FIND-NNN'.format(label))
        for r in refs:
            if r not in known_ids:
                err('{}: references missing {}'.format(label, r))

    # retests
    for r in art['retests']:
        label = 'retest "{}"'.format(r['heading'])
        res = r['fields'].get('Result', '').strip()
        if res not in RETEST_STATUSES:
            err('{}: invalid or missing Result "{}" (allowed: {})'.format(
                label, res, ', '.join(RETEST_STATUSES)))
        elif res in ('FIX_VERIFIED', 'STILL_FAILING') and is_empty_val(r['fields'].get('Evidence')):
            err('{}: result {} requires non-empty Evidence'.format(label, res))

    # final verdict
    verdict = art['verdict'].get('Verdict', '').strip()
    if verdict not in VERDICTS:
        err('Final Verdict: invalid or missing Verdict "{}"'.format(verdict))
    else:
        if verdict == 'PASS' and (counts['FAIL'] or counts['BLOCKED'] or counts['NEEDS_VERIFICATION']):
            err('Final Verdict PASS is inconsistent with checks '
                '(FAIL:{} BLOCKED:{} NEEDS_VERIFICATION:{})'.format(
                    counts['FAIL'], counts['BLOCKED'], counts['NEEDS_VERIFICATION']))
        if verdict == 'FAIL' and counts['FAIL'] == 0:
            err('Final Verdict FAIL but no check has status FAIL')
    rec = art['verdict'].get('Recommendation', '').strip()
    if rec and not rec.startswith('<') and rec not in RECOMMENDATIONS:
        err('Final Verdict: invalid Recommendation "{}"'.format(rec))
    if rec == 'READY' and verdict != 'PASS':
        err('Recommendation READY requires Verdict PASS (got {})'.format(verdict or 'none'))

    # secrets
    for pattern, what in SECRET_PATTERNS:
        m = pattern.search(content)
        if m:
            err('{} detected ("{}..."); secrets must not be stored in QA artifacts'.format(
                what, m.group(0)[:24]))

    return {'file': file, 'errors': errors, 'warnings': warnings,
            'counts': counts, 'verdict': verdict, 'art': art}

# ---------- commands ----------

def rel(f):
    return os.path.relpath(f, ROOT).replace('\\', '/')


def cmd_validate(args):
    targets = [os.path.abspath(os.path.join(ROOT, a)) for a in args] if args \
        else all_artifacts(VALIDATE_DIRS)
    if not targets:
        print('No QA work artifacts found.')
        return 0
    failed = 0
    for f in targets:
        if not os.path.exists(f):
            print('ERROR {}: file not found'.format(f), file=sys.stderr)
            failed += 1
            continue
        r = validate_artifact(f)
        if r['errors']:
            failed += 1
            print('INVALID  {}'.format(rel(f)))
            for e in r['errors']:
                print('  error: {}'.format(e))
        else:
            print('OK       {}'.format(rel(f)))
        for w in r['warnings']:
            print('  warn:  {}'.format(w))
    print('\n{} artifact(s), {} invalid.'.format(len(targets), failed))
    return 1 if failed else 0


def cmd_find(terms):
    if not terms:
        print('Usage: gqa.py find <query terms>', file=sys.stderr)
        return 1
    q = [t.lower() for t in terms]
    results = []
    for f in all_artifacts(OPERATIONAL_DIRS):
        with open(f, encoding='utf-8') as fh:
            content = fh.read().lower()
        name = rel(f).lower()
        score = 0
        for t in q:
            if t in name:
                score += 5
            hits = content.count(t)
            score += min(hits, 5)
        if all(t in name or t in content for t in q):
            score += 10
        if score > 0:
            results.append((f, score))
    results.sort(key=lambda x: -x[1])
    if not results:
        print('No saved QA work matches the query.')
        return 0
    for f, score in results[:10]:
        with open(f, encoding='utf-8') as fh:
            art = parse_artifact(fh.read())
        print('{}\t{}\t{}\t[{}]'.format(
            score, rel(f), art['title'] or '',
            (art['verdict'].get('Verdict') or '?').strip()))
    return 0


def cmd_list(args):
    open_only = '--open' in args
    rows = []
    for f in all_artifacts(OPERATIONAL_DIRS):
        r = validate_artifact(f)
        v = r['verdict'] or '?'
        is_open = v != 'PASS'
        if open_only and not is_open:
            continue
        c = r['counts']
        rows.append({
            'file': rel(f), 'title': r['art']['title'] or '', 'verdict': v or '?',
            'checks': 'P:{} F:{} B:{} NV:{}'.format(
                c['PASS'], c['FAIL'], c['BLOCKED'], c['NEEDS_VERIFICATION']),
            'valid': 'INVALID' if r['errors'] else 'ok',
        })
    if not rows:
        print('No open QA work.' if open_only else 'No QA work artifacts found.')
        return 0
    for r in rows:
        print('{} {} {} {}  — {}'.format(
            r['verdict'].ljust(19), r['checks'].ljust(22),
            r['valid'].ljust(8), r['file'], r['title']))
    return 0

# ---------- main ----------

def main(argv):
    cmd = argv[1] if len(argv) > 1 else None
    rest = argv[2:]
    if cmd == 'validate':
        return cmd_validate(rest)
    if cmd == 'find':
        return cmd_find(rest)
    if cmd == 'list':
        return cmd_list(rest)
    print('Usage: python scripts/gqa.py <validate [paths]|find <query>|list [--open]>',
          file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))

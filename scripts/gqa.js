#!/usr/bin/env node
/*
 * Deterministic guardrails for the General QA Pipeline.
 * Zero dependencies. Node >= 16.
 *
 * Usage:
 *   node scripts/gqa.js validate [path ...]   # default: all artifacts in work/ and examples/
 *   node scripts/gqa.js find <query terms>    # search saved QA work
 *   node scripts/gqa.js list [--open]         # list QA work with verdicts
 *
 * Exit codes: 0 ok, 1 validation errors / bad usage.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
// validate covers synthetic examples too; find/list operate on real QA work only
const VALIDATE_DIRS = ['work', 'examples'];
const OPERATIONAL_DIRS = ['work'];

const CHECK_STATUSES = ['PASS', 'FAIL', 'BLOCKED', 'NEEDS_VERIFICATION'];
const RETEST_STATUSES = ['FIX_VERIFIED', 'STILL_FAILING', 'BLOCKED', 'NEEDS_VERIFICATION'];
const VERDICTS = ['PASS', 'FAIL', 'BLOCKED', 'NEEDS_VERIFICATION'];
const SCOPE_STATES = ['APPLICABLE', 'N/A', 'ONLY_ON_FAILURE', 'UNAVAILABLE'];
const CLASSIFICATIONS = ['PRODUCT_DEFECT', 'REQUIREMENT_AMBIGUITY', 'ENVIRONMENT', 'TEST_DATA', 'AGENT_FALSE_POSITIVE', 'UNKNOWN'];
const RECOMMENDATIONS = ['READY', 'NOT_READY', 'NEEDS_VERIFICATION'];

const SECRET_PATTERNS = [
  [/bearer\s+[a-z0-9._\-]{16,}/i, 'possible bearer token'],
  [/api[_-]?key\s*[:=]\s*[^\s<*]{8,}/i, 'possible API key'],
  [/password\s*[:=]\s*[^\s<*]{4,}/i, 'possible password'],
  [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, 'private key'],
  [/\bsk-[a-zA-Z0-9]{20,}/, 'possible secret key'],
  [/eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}/, 'possible JWT'],
  [/(session|auth)[_-]?token\s*[:=]\s*[^\s<*]{8,}/i, 'possible session token'],
];

// ---------- artifact discovery ----------

function isQaWork(content) {
  return /^# QA Work:/m.test(content);
}

function walkMd(dir, acc) {
  if (!fs.existsSync(dir)) return acc;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === 'node_modules' || e.name.startsWith('.')) continue;
      walkMd(p, acc);
    } else if (e.name.endsWith('.md')) {
      acc.push(p);
    }
  }
  return acc;
}

function allArtifacts(dirs) {
  const files = [];
  for (const d of dirs) walkMd(path.join(ROOT, d), files);
  return files.filter((f) => {
    try { return isQaWork(fs.readFileSync(f, 'utf8')); } catch { return false; }
  });
}

// ---------- parsing ----------

function parseArtifact(content) {
  const lines = content.split(/\r?\n/);
  const art = {
    title: null, meta: {}, scope: {}, checks: [], findings: [], defects: [],
    retests: [], verdict: {}, idHeadings: [], sections: new Set(),
  };
  let section = null;
  let block = null; // current ### block: {kind, id, fields}

  const flush = () => {
    if (!block) return;
    if (block.kind === 'check') art.checks.push(block);
    else if (block.kind === 'finding') art.findings.push(block);
    else if (block.kind === 'defect') art.defects.push(block);
    else if (block.kind === 'retest') art.retests.push(block);
    block = null;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let m;
    if ((m = line.match(/^# QA Work:\s*(.*)/))) { art.title = m[1].trim(); continue; }
    if ((m = line.match(/^## (.+)/))) {
      flush();
      section = m[1].trim();
      art.sections.add(section);
      continue;
    }
    if ((m = line.match(/^### (.+)/))) {
      flush();
      const h = m[1].trim();
      const id = (h.match(/\b(REQ|CHK|FIND|DEF)-\d{3}\b/) || [])[0] || null;
      if (id) art.idHeadings.push({ id, line: i + 1 });
      block = {
        kind: section === 'Checks' ? 'check'
          : section === 'Findings' ? 'finding'
          : section === 'Defects' ? 'defect'
          : section === 'Retest History' ? 'retest' : 'other',
        id, heading: h, line: i + 1, fields: {},
      };
      continue;
    }
    if ((m = line.match(/^- ([A-Za-z /]+):\s*(.*)$/))) {
      const key = m[1].trim();
      const val = m[2].trim();
      if (block) block.fields[key] = val;
      else if (section === 'Metadata') art.meta[key] = val;
      else if (section === 'Verification Scope') art.scope[key] = val;
      else if (section === 'Final Verdict') art.verdict[key] = val;
      continue;
    }
    // REQ list items: "- REQ-001: ..."
    if ((m = line.match(/^- (REQ-\d{3}):/))) {
      art.idHeadings.push({ id: m[1], line: i + 1 });
    }
  }
  flush();
  return art;
}

// ---------- validation ----------

const isEmptyVal = (v) => !v || /^(-|none|n\/a|<.*>)$/i.test(v.trim());

function validateArtifact(file) {
  const errors = [];
  const warnings = [];
  const content = fs.readFileSync(file, 'utf8');
  const art = parseArtifact(content);
  const err = (msg) => errors.push(msg);
  const warn = (msg) => warnings.push(msg);

  if (!art.title) err('missing "# QA Work: <title>" heading');

  // duplicate IDs
  const seen = new Map();
  for (const { id, line } of art.idHeadings) {
    if (seen.has(id)) err(`duplicate ID ${id} (lines ${seen.get(id)} and ${line})`);
    else seen.set(id, line);
  }
  const knownIds = new Set(seen.keys());

  // required sections
  for (const s of ['Metadata', 'Source', 'Checks', 'Final Verdict']) {
    if (!art.sections.has(s)) err(`missing required section "## ${s}"`);
  }

  // verification scope states
  for (const [layer, val] of Object.entries(art.scope)) {
    const v = val.split('—')[0].split(' - ')[0].trim();
    if (v && !v.startsWith('<') && !SCOPE_STATES.includes(v)) {
      err(`Verification Scope ${layer}: invalid state "${v}" (allowed: ${SCOPE_STATES.join(', ')})`);
    }
  }

  // checks
  const counts = { PASS: 0, FAIL: 0, BLOCKED: 0, NEEDS_VERIFICATION: 0 };
  for (const c of art.checks) {
    const label = c.id || `check at line ${c.line}`;
    const status = (c.fields['Status'] || '').trim();
    if (!CHECK_STATUSES.includes(status)) {
      err(`${label}: invalid or missing Status "${status}" (allowed: ${CHECK_STATUSES.join(', ')})`);
    } else {
      counts[status]++;
      if ((status === 'PASS' || status === 'FAIL') && isEmptyVal(c.fields['Evidence'])) {
        err(`${label}: status ${status} requires non-empty Evidence`);
      }
    }
    const req = (c.fields['Requirement'] || '').trim();
    if (req && !isEmptyVal(req)) {
      for (const r of req.split(/[,\s]+/).filter((x) => /^REQ-\d{3}$/.test(x))) {
        if (!knownIds.has(r)) err(`${label}: references missing ${r}`);
      }
    }
    if (isEmptyVal(c.fields['Oracle'])) warn(`${label}: no Oracle recorded`);
  }

  // defects
  for (const d of art.defects) {
    const label = d.id || `defect at line ${d.line}`;
    const cls = (d.fields['Classification'] || '').trim();
    if (!CLASSIFICATIONS.includes(cls)) {
      err(`${label}: invalid or missing Classification "${cls}"`);
    }
    const finds = (d.fields['Findings'] || '').trim();
    const refs = finds.split(/[,\s]+/).filter((x) => /^FIND-\d{3}$/.test(x));
    if (refs.length === 0) err(`${label}: must reference at least one FIND-NNN`);
    for (const r of refs) if (!knownIds.has(r)) err(`${label}: references missing ${r}`);
  }

  // retests
  for (const r of art.retests) {
    const label = `retest "${r.heading}"`;
    const res = (r.fields['Result'] || '').trim();
    if (!RETEST_STATUSES.includes(res)) {
      err(`${label}: invalid or missing Result "${res}" (allowed: ${RETEST_STATUSES.join(', ')})`);
    } else if ((res === 'FIX_VERIFIED' || res === 'STILL_FAILING') && isEmptyVal(r.fields['Evidence'])) {
      err(`${label}: result ${res} requires non-empty Evidence`);
    }
  }

  // final verdict
  const verdict = (art.verdict['Verdict'] || '').trim();
  if (!VERDICTS.includes(verdict)) {
    err(`Final Verdict: invalid or missing Verdict "${verdict}"`);
  } else {
    if (verdict === 'PASS' && (counts.FAIL || counts.BLOCKED || counts.NEEDS_VERIFICATION)) {
      err(`Final Verdict PASS is inconsistent with checks (FAIL:${counts.FAIL} BLOCKED:${counts.BLOCKED} NEEDS_VERIFICATION:${counts.NEEDS_VERIFICATION})`);
    }
    if (verdict === 'FAIL' && counts.FAIL === 0) {
      err('Final Verdict FAIL but no check has status FAIL');
    }
  }
  const rec = (art.verdict['Recommendation'] || '').trim();
  if (rec && !rec.startsWith('<') && !RECOMMENDATIONS.includes(rec)) {
    err(`Final Verdict: invalid Recommendation "${rec}"`);
  }
  if (rec === 'READY' && verdict !== 'PASS') {
    err(`Recommendation READY requires Verdict PASS (got ${verdict || 'none'})`);
  }

  // secrets
  for (const [re, what] of SECRET_PATTERNS) {
    const m = content.match(re);
    if (m) err(`${what} detected ("${m[0].slice(0, 24)}..."); secrets must not be stored in QA artifacts`);
  }

  return { file, errors, warnings, counts, verdict, art };
}

// ---------- commands ----------

function rel(f) { return path.relative(ROOT, f).replace(/\\/g, '/'); }

function cmdValidate(args) {
  const targets = args.length
    ? args.map((a) => path.resolve(ROOT, a))
    : allArtifacts(VALIDATE_DIRS);
  if (!targets.length) { console.log('No QA work artifacts found.'); return 0; }
  let failed = 0;
  for (const f of targets) {
    if (!fs.existsSync(f)) { console.error(`ERROR ${f}: file not found`); failed++; continue; }
    const r = validateArtifact(f);
    if (r.errors.length) {
      failed++;
      console.log(`INVALID  ${rel(f)}`);
      for (const e of r.errors) console.log(`  error: ${e}`);
    } else {
      console.log(`OK       ${rel(f)}`);
    }
    for (const w of r.warnings) console.log(`  warn:  ${w}`);
  }
  console.log(`\n${targets.length} artifact(s), ${failed} invalid.`);
  return failed ? 1 : 0;
}

function cmdFind(terms) {
  if (!terms.length) { console.error('Usage: gqa.js find <query terms>'); return 1; }
  const q = terms.map((t) => t.toLowerCase());
  const results = [];
  for (const f of allArtifacts(OPERATIONAL_DIRS)) {
    const content = fs.readFileSync(f, 'utf8').toLowerCase();
    const name = rel(f).toLowerCase();
    let score = 0;
    for (const t of q) {
      if (name.includes(t)) score += 5;
      const hits = content.split(t).length - 1;
      score += Math.min(hits, 5);
    }
    if (q.every((t) => name.includes(t) || content.includes(t))) score += 10;
    if (score > 0) results.push({ f, score });
  }
  results.sort((a, b) => b.score - a.score);
  if (!results.length) { console.log('No saved QA work matches the query.'); return 0; }
  for (const { f, score } of results.slice(0, 10)) {
    const art = parseArtifact(fs.readFileSync(f, 'utf8'));
    console.log(`${score}\t${rel(f)}\t${art.title || ''}\t[${(art.verdict['Verdict'] || '?').trim()}]`);
  }
  return 0;
}

function cmdList(args) {
  const openOnly = args.includes('--open');
  const rows = [];
  for (const f of allArtifacts(OPERATIONAL_DIRS)) {
    const r = validateArtifact(f);
    const v = r.verdict || '?';
    const open = v !== 'PASS';
    if (openOnly && !open) continue;
    rows.push({
      file: rel(f), title: r.art.title || '', verdict: v || '?',
      checks: `P:${r.counts.PASS} F:${r.counts.FAIL} B:${r.counts.BLOCKED} NV:${r.counts.NEEDS_VERIFICATION}`,
      valid: r.errors.length ? 'INVALID' : 'ok',
    });
  }
  if (!rows.length) { console.log(openOnly ? 'No open QA work.' : 'No QA work artifacts found.'); return 0; }
  for (const r of rows) {
    console.log(`${r.verdict.padEnd(19)} ${r.checks.padEnd(22)} ${r.valid.padEnd(8)} ${r.file}  — ${r.title}`);
  }
  return 0;
}

// ---------- main ----------

const [, , cmd, ...rest] = process.argv;
let code;
switch (cmd) {
  case 'validate': code = cmdValidate(rest); break;
  case 'find': code = cmdFind(rest); break;
  case 'list': code = cmdList(rest); break;
  default:
    console.error('Usage: node scripts/gqa.js <validate [paths]|find <query>|list [--open]>');
    code = 1;
}
process.exit(code);

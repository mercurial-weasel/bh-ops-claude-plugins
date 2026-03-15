#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { buildProposal } = require('./builder');
const { SERVICE_LINE_DEFAULTS, DEFAULT_AGENDA, COMMON_DEFAULTS } = require('./template');
const schema = require('./params-schema.json');

const OUTPUT_DIR = path.join(__dirname, 'output');
const LAST_REF_FILE = path.join(OUTPUT_DIR, '.last-ref');

// ============================================================
// CLI argument parsing
// ============================================================

function parseArgs() {
  const args = process.argv.slice(2);
  const mode = { type: null, value: null };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--params' && args[i + 1]) {
      mode.type = 'file';
      mode.value = args[i + 1];
      i++;
    } else if (args[i] === '--json' && args[i + 1]) {
      mode.type = 'json';
      mode.value = args[i + 1];
    } else if (args[i] === '--interactive') {
      mode.type = 'interactive';
    }
  }

  if (!mode.type) {
    console.error('Usage:');
    console.error('  node generate.js --params ./params.json');
    console.error('  node generate.js --json \'{"client_name": "...", ...}\'');
    console.error('  node generate.js --interactive');
    process.exit(1);
  }

  return mode;
}

// ============================================================
// Auto-increment proposal ref
// ============================================================

function getNextRef() {
  const year = new Date().getFullYear();
  let seq = 1;

  if (fs.existsSync(LAST_REF_FILE)) {
    const last = fs.readFileSync(LAST_REF_FILE, 'utf8').trim();
    const match = last.match(/^BH-(\d{4})-(\d+)$/);
    if (match && parseInt(match[1]) === year) {
      seq = parseInt(match[2]) + 1;
    }
  }

  const ref = `BH-${year}-${String(seq).padStart(3, '0')}`;
  fs.writeFileSync(LAST_REF_FILE, ref);
  return ref;
}

// ============================================================
// Date helpers
// ============================================================

function formatDate(date) {
  return date.toLocaleDateString('en-NZ', { day: 'numeric', month: 'long', year: 'numeric' });
}

function addDays(date, days) {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
}

// ============================================================
// Validate params against schema
// ============================================================

function validate(params) {
  const errors = [];
  const required = schema.required || [];

  for (const field of required) {
    if (!params[field] || (typeof params[field] === 'string' && params[field].trim() === '')) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  if (params.service_line) {
    const allowed = schema.properties.service_line.enum;
    if (!allowed.includes(params.service_line)) {
      errors.push(`Invalid service_line "${params.service_line}". Must be one of: ${allowed.join(', ')}`);
    }
  }

  if (params.agenda) {
    for (let i = 0; i < params.agenda.length; i++) {
      const item = params.agenda[i];
      if (!item.time || !item.item) {
        errors.push(`Agenda item ${i + 1} must have "time" and "item" fields`);
      }
    }
  }

  return errors;
}

// ============================================================
// Merge defaults with provided params
// ============================================================

function mergeParams(userParams) {
  const now = new Date();
  const serviceLine = userParams.service_line || 'generic';
  const serviceDefaults = SERVICE_LINE_DEFAULTS[serviceLine] || SERVICE_LINE_DEFAULTS.generic;

  // Layer: common defaults → service line defaults → user params
  const merged = {
    ...COMMON_DEFAULTS,
    ...serviceDefaults,
    proposal_date: formatDate(now),
    proposal_ref: getNextRef(),
    proposal_expiry: formatDate(addDays(now, 30)),
    agenda: DEFAULT_AGENDA,
    ...userParams,
  };

  return merged;
}

// ============================================================
// Interactive mode (basic readline prompts)
// ============================================================

async function interactiveMode() {
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise(resolve => rl.question(q, resolve));

  console.log('\n--- Blue Harbour Proposal Generator ---\n');

  const params = {};
  params.client_name = await ask('Client name: ');
  params.client_contact = await ask('Contact name: ');
  params.client_title = await ask('Contact title: ');
  params.client_email = await ask('Contact email (optional): ') || undefined;
  params.service_line = await ask('Service line (capital_planning / ai_agents / reporting / data_enablement / generic): ');
  params.workshop_title = await ask('Workshop title (enter to use default): ') || undefined;
  params.proposed_date = await ask('Proposed date (e.g. "Week of 6 April 2026"): ') || undefined;
  params.follow_on_indicative = await ask('Indicative follow-on (e.g. "$15,000-$25,000 NZD"): ') || undefined;

  rl.close();

  // Clean undefined values
  Object.keys(params).forEach(k => { if (params[k] === undefined) delete params[k]; });

  return params;
}

// ============================================================
// Main
// ============================================================

async function main() {
  const mode = parseArgs();
  let userParams;

  switch (mode.type) {
    case 'file': {
      const filePath = path.resolve(mode.value);
      if (!fs.existsSync(filePath)) {
        console.error(`File not found: ${filePath}`);
        process.exit(1);
      }
      userParams = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      break;
    }
    case 'json': {
      try {
        userParams = JSON.parse(mode.value);
      } catch (e) {
        console.error(`Invalid JSON: ${e.message}`);
        process.exit(1);
      }
      break;
    }
    case 'interactive': {
      userParams = await interactiveMode();
      break;
    }
  }

  // Merge defaults
  const params = mergeParams(userParams);

  // Validate
  const errors = validate(params);
  if (errors.length > 0) {
    console.error('Validation errors:');
    errors.forEach(e => console.error(`  - ${e}`));
    process.exit(1);
  }

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Build document
  const buffer = await buildProposal(params);

  // Write file
  const filename = `BH-Proposal-${params.client_name.replace(/\s+/g, '-')}-${params.proposal_ref}.docx`;
  const outputPath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(outputPath, buffer);

  // Output summary
  console.log(`\n\u2713 Proposal generated`);
  console.log(`  File: ${outputPath}`);
  console.log(`  Client: ${params.client_name} / ${params.client_contact}`);
  console.log(`  Service line: ${params.service_line_label || params.service_line}`);
  console.log(`  Ref: ${params.proposal_ref}`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});

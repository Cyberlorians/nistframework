const fs = require('fs');
const html = fs.readFileSync('docs/index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) { console.log('No script tag found!'); process.exit(1); }
const js = scriptMatch[1];

// Check brace balance
let braces = 0, parens = 0, brackets = 0;
let inString = false, stringChar = '', escaped = false;
for (let i = 0; i < js.length; i++) {
  const ch = js[i];
  if (escaped) { escaped = false; continue; }
  if (ch === '\\') { escaped = true; continue; }
  if (inString) { if (ch === stringChar) inString = false; continue; }
  if (ch === '"' || ch === "'" || ch === '`') { inString = true; stringChar = ch; continue; }
  if (ch === '{') braces++;
  if (ch === '}') braces--;
  if (ch === '(') parens++;
  if (ch === ')') parens--;
  if (ch === '[') brackets++;
  if (ch === ']') brackets--;
}
console.log('Braces balance:', braces, '(should be 0)');
console.log('Parens balance:', parens, '(should be 0)');  
console.log('Brackets balance:', brackets, '(should be 0)');

// Check for common issues
const lines = js.split('\n');
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  // Check for literal newlines inside quotes (broken strings)
  if (line.match(/= ['"][^'"]*$/)) {
    console.log('POSSIBLE BROKEN STRING at line', i+1, ':', line.trim().substring(0, 80));
  }
}

// Try to actually parse the JS with Function constructor
try {
  new Function(js);
  console.log('JS syntax: VALID');
} catch(e) {
  console.log('JS syntax: INVALID -', e.message);
}

// Check for issues specific to browser rendering
// Look for template literals with ${} that might have been rendered by Python
const templateIssues = js.match(/\$\{[^}]+\}/g);
if (templateIssues) {
  console.log('Template literals found:', templateIssues.length);
  // Check if any look like unresolved Python expressions
  templateIssues.forEach(t => {
    if (t.includes('  ') || t.includes('__')) {
      console.log('  Suspicious template:', t);
    }
  });
}

// Check for undefined variable references in event bindings area
const eventBindingStart = js.indexOf('// ─── Event bindings');
if (eventBindingStart >= 0) {
  const eventSection = js.substring(eventBindingStart);
  console.log('\nEvent binding section (last', eventSection.split('\n').length, 'lines):');
  console.log('---');
  eventSection.split('\n').slice(0, 20).forEach((l, i) => console.log(i + ':', l));
}

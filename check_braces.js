const fs = require('fs');
const html = fs.readFileSync('docs/index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
const js = scriptMatch[1];

let braces = 0, parens = 0;
let inString = false, stringChar = '', escaped = false;
const lines = js.split('\n');

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  let lineBraceChange = 0, lineParenChange = 0;
  for (let j = 0; j < line.length; j++) {
    const ch = line[j];
    if (escaped) { escaped = false; continue; }
    if (ch === '\\') { escaped = true; continue; }
    if (inString) { if (ch === stringChar) inString = false; continue; }
    if (ch === '"' || ch === "'" || ch === '`') { inString = true; stringChar = ch; continue; }
    if (ch === '{') { braces++; lineBraceChange++; }
    if (ch === '}') { braces--; lineBraceChange--; }
    if (ch === '(') { parens++; lineParenChange++; }
    if (ch === ')') { parens--; lineParenChange--; }
  }
  // Report lines where balance changes significantly
  if (lineBraceChange !== 0 || lineParenChange !== 0) {
    if (braces < 0 || parens < 0) {
      console.log('LINE', i+1, '| braces:', braces, 'parens:', parens, '|', line.trim().substring(0, 100));
    }
  }
}

// Now find lines where functions start and track their nesting
console.log('\n--- Final balance: braces=' + braces + ' parens=' + parens + ' ---');

// Find the specific functions and their brace counts
const funcRegex = /^function (\w+)/;
let currentFunc = null;
let funcBraces = 0;
braces = 0; parens = 0;
inString = false; escaped = false;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const funcMatch = line.match(funcRegex);
  if (funcMatch && !inString) {
    if (currentFunc && braces > 0) {
      console.log('UNCLOSED FUNCTION:', currentFunc, 'at line', i+1, 'braces remaining:', braces);
    }
    currentFunc = funcMatch[1];
    // Don't reset braces - track running total
  }
  
  for (let j = 0; j < line.length; j++) {
    const ch = line[j];
    if (escaped) { escaped = false; continue; }
    if (ch === '\\') { escaped = true; continue; }
    if (inString) { if (ch === stringChar) inString = false; continue; }
    if (ch === '"' || ch === "'" || ch === '`') { inString = true; stringChar = ch; continue; }
    if (ch === '{') braces++;
    if (ch === '}') braces--;
    if (ch === '(') parens++;
    if (ch === ')') parens--;
  }
}
if (braces > 0) console.log('Script ends with', braces, 'unclosed braces');
if (parens > 0) console.log('Script ends with', parens, 'unclosed parens');

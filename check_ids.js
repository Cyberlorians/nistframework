const fs = require('fs');
const html = fs.readFileSync('docs/index.html', 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const js = m[1];

// Find all getElementById calls and check if the target element exists
const re = /getElementById\('([^']+)'\)/g;
let match;
const checked = new Set();
while ((match = re.exec(js)) !== null) {
  const id = match[1];
  if (checked.has(id)) continue;
  checked.add(id);
  // Check for dynamic IDs (contain + or variable references)
  if (id.includes('+') || id.includes('${')) continue;
  const found = html.includes('id="' + id + '"');
  if (!found) {
    // Find line number
    const pos = match.index;
    const lineNum = js.substring(0, pos).split('\n').length;
    console.log('MISSING id="' + id + '" at script line ' + lineNum);
  }
}

// Also check for dynamic getElementById patterns
const dynRe = /getElementById\(([^)]+)\)/g;
while ((match = dynRe.exec(js)) !== null) {
  const arg = match[1].trim();
  if (arg.startsWith("'") && arg.endsWith("'")) continue; // static, already checked
  // Dynamic - just report
  const pos = match.index;
  const lineNum = js.substring(0, pos).split('\n').length;
  // console.log('DYNAMIC getElementById at line ' + lineNum + ': ' + arg);
}

console.log('Done checking ' + checked.size + ' static element IDs');

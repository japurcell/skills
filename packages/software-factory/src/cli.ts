#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--help') {
  process.stdout.write('software-factory (development)\nRuntime commands are not implemented yet.\n');
} else {
  process.stderr.write('software-factory: runtime commands not implemented; startup refused\n');
  process.exitCode = 3;
}

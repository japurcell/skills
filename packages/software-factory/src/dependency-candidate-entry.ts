import { prepareDependencyCandidateRequest } from './dependency-candidate.js';

if (process.argv.length !== 4 || process.argv[2] !== '--request') throw new Error('fixed private dependency candidate request required');
try {
  const receipt = await prepareDependencyCandidateRequest(process.argv[3]!);
  const output = `${JSON.stringify(receipt)}\n`;
  if (Buffer.byteLength(output) > 4096) throw new Error('dependency candidate receipt exceeds bound');
  process.stdout.write(output);
} catch {
  // Private request/claim paths and tokens must never appear in bootstrap output.
  process.stderr.write('dependency candidate preparation refused; claim and evidence retained\n');
  process.exitCode = 1;
}

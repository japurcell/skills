import { constants, cpSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const PACKAGE_NAMES = ['typescript', '@types/node', 'undici-types'];

export function copyLearningToolchain(source, destination) {
  mkdirSync(destination);
  const names = [...PACKAGE_NAMES, `@typescript/typescript-${process.platform}-${process.arch}`];
  for (const name of names) {
    const target = join(destination, name);
    mkdirSync(dirname(target), { recursive: true });
    cpSync(join(source, name), target, {
      recursive: true,
      dereference: true,
      mode: constants.COPYFILE_FICLONE,
    });
  }
}

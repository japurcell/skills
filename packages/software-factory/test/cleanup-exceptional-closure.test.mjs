import test from 'node:test';
import { exceptionalClosure } from '../qualification/cleanup-exceptional-public.qualification.mjs';

test('exceptional selection reports the genuine action chain', t => exceptionalClosure(t));

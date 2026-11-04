import test from 'node:test';
import { actionClosureFixture, actionClosureTampering } from '../qualification/cleanup-actions-public.qualification.mjs';

test('genuine library action reports retain all outcomes and digest-bound recursive evidence', t => actionClosureFixture(t, { installed: false, probe: actionClosureTampering }));

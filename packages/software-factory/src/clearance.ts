import type { Claim, RepositoryStore } from './store.js';
import { inspectOwner } from './native/process.js';
import { environmentRedactionPolicy, redactText } from './redaction.js';

export function inspectClaim(store: RepositoryStore, claim: Claim) {
  const owner = inspectOwner(claim.owner);
  const activity = claim.invocationId ? store.inspectActivity(claim.invocationId) : {attempts:[],hasMore:false};
  const scopes = activity.attempts.map(attempt => ({attemptId:attempt.id,launch:attempt.launch,
    inspection:attempt.owner ? inspectOwner(attempt.owner) : {state:'unknown',limitation:'launch/start identity unavailable'},
    limitation:'owned process absence does not establish escaped or remote descendant cleanup'}));
  const state = owner.state === 'known_live' || scopes.some(scope => scope.inspection.state === 'known_live') ? 'known_live'
    : owner.state === 'unknown' || scopes.length || activity.hasMore ? 'unknown' : 'not_live';
  return {claim,inspection:{state,owner,scopes,moreScopes:activity.hasMore,limitation:'inspection never signals stored PIDs; operator confirms unsupported child cleanup'}};
}
export async function clearClaim(store: RepositoryStore, input: {claimId:string;token:string;operatorConfirmed:boolean;note:string}) {
  const claim = store.readClaim(input.claimId);
  if (claim.token !== input.token) throw new Error('claim/token no longer matches');
  const inspected = inspectClaim(store,claim);
  if (inspected.inspection.state === 'known_live') throw new Error('known-live owner or scope cannot be cleared');
  const note = redactText(input.note,environmentRedactionPolicy());
  return store.clearOwner({...input,note,inspection:inspected.inspection.state as 'not_live'|'unknown',details:inspected.inspection});
}

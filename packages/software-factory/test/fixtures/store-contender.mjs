import { openRepositoryStore } from '../../dist/store.js';

const store = openRepositoryStore(process.argv[2]);
process.send({ ready: true });
process.once('message', async ({ action, input }) => {
  let paused = false;
  try {
    let value;
    if (action === 'crash-before' || action === 'crash-after') {
      if (action === 'crash-after') await store.admitAttempt(input);
      paused = true;
      const hold = setInterval(() => {}, 1000);
      process.once('disconnect', () => { clearInterval(hold); store.close(); });
      process.send({ point: action === 'crash-before' ? 'before' : 'after' });
      return;
    }
    if (action === 'invocation') value = await store.startInvocation(input);
    else if (action === 'admit') value = await store.admitAttempt(input);
    else if (action === 'claim') value = await store.claimResource(input);
    else throw new Error('unknown fixture action');
    process.send({ ok: true, value });
  } catch (error) {
    process.send({ ok: false, error: error.message });
  } finally {
    if (!paused) {
      store.close();
      process.disconnect();
    }
  }
});

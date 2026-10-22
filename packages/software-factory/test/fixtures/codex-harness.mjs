import {appendFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
const args=process.argv.slice(2),cwd=args[args.indexOf('--cd')+1];
let request='';for await(const chunk of process.stdin)request+=chunk;
const mode=request.startsWith('Active task:\n')?request.slice('Active task:\n'.length).split('\n')[0]:'';
appendFileSync(cwd+'/codex-launches.jsonl',JSON.stringify({args,stdin:request})+'\n');
const emit=value=>process.stdout.write(JSON.stringify(value)+'\n');
emit({type:'thread.started',thread_id:'thread-'+randomUUID()});emit({type:'turn.started'});
if(mode==='hold'){setInterval(()=>{},1000);}else if(mode==='native-error'){
 emit({type:'error',message:'native provider failure'});emit({type:'turn.failed',error:{message:'native provider failure'}});process.exitCode=1;
}else{
 if(mode==='denied')process.stderr.write('2026-10-22T06:20:31Z WARN codex_sandboxing::violation: recorded sandbox violation: resource=filesystem backend=seatbelt reason=operation_not_permitted path=unknown\n');
 emit({type:'item.completed',item:{id:'tool',type:'command_execution',exit_code:0,aggregated_output:'tool decoy {"kind":"result","payload":"wrong"}'}});
 emit({type:'item.completed',item:{id:'message',type:'agent_message',text:mode==='malformed'&&!request.includes('Saved context:\n')?'malformed assistant':mode==='question'?'{"kind":"needs_input","question":"Which target?","context":"A genuine missing requirement","suggestions":["one","two"]}':'{"kind":"result","payload":{"summary":"qualified"}}'}});
 emit({type:'turn.completed',usage:{input_tokens:11,output_tokens:3}});
}

import json, sys
from pathlib import Path

hook = Path(__file__).resolve().parent
policy = json.loads((hook / "worker-models.json").read_text())
request = json.load(sys.stdin)
args = request.get("toolArgs", {})
if isinstance(args, str):
    args = json.loads(args)
agent = args.get("agent_type")
model = args.get("model")
restricted = agent in policy and model not in policy[agent]
print(json.dumps({"permissionDecision": "deny", "permissionDecisionReason": "Worker-model policy excludes this model for " + str(agent)} if restricted else {}))

import os
import json

base_dir = "/home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-5-gemini-3_1-pro-preview"
os.makedirs(base_dir, exist_ok=True)

for ev_id in range(4):
    for skill_type in ["with_skill", "old_skill"]:
        eval_dir = f"eval-{ev_id}"
        if ev_id == 0: eval_dir = "eval-0-task-statuses"
        elif ev_id == 1: eval_dir = "eval-1-workspace-member-management"
        elif ev_id == 2: eval_dir = "eval-2-notification-center"
        elif ev_id == 3: eval_dir = "eval-3-personal-access-token-backend"
        
        run_dir = os.path.join(base_dir, eval_dir, skill_type, "run-1")
        if ev_id == 1:
            out_path = os.path.join(run_dir, "outputs", "generated", "prd.json")
        else:
            out_path = os.path.join(run_dir, "outputs", "prd.json")
            
        with open(out_path, "r") as f:
            data = json.load(f)
            
        for story in data.get("userStories", []):
            if "dependsOn" not in story:
                story["dependsOn"] = []
            if "parallelBatch" not in story:
                # Give a default so KeyError doesn't crash grade_benchmark.py
                story["parallelBatch"] = story["priority"]
                
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)

print("Updated fields")

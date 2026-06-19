import json

path = "/home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-5-gemini-3_1-pro-preview/benchmark.json"
with open(path, "r") as f:
    data = json.load(f)

if "metadata" not in data:
    data["metadata"] = {}
data["metadata"]["executor_model"] = "gemini-3.1-pro-preview"
data["metadata"]["analyzer_model"] = "gemini-3.1-pro-preview"

with open(path, "w") as f:
    json.dump(data, f, indent=2)

md_path = "/home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-5-gemini-3_1-pro-preview/benchmark.md"
with open(md_path, "r") as f:
    content = f.read()

content = content.replace("**Model**: gpt-4o", "**Model**: gemini-3.1-pro-preview")
content = content.replace("**Model**: <model-name>", "**Model**: gemini-3.1-pro-preview")

with open(md_path, "w") as f:
    f.write(content)

import json
from model_adapters import call_llm

SYSTEM = """
You are a React/Vite build fixing expert.

Input:
1. Build error
2. Project files

Return ONLY JSON:

{
  "fixes":[
    {
      "file_path":"",
      "updated_code":""
    }
  ]
}
"""

def fix_build(error_log, files):

    payload = json.dumps({
        "error": error_log,
        "files": files
    })

    result = call_llm(
        payload,
        agent="buildfix",
        system_prompt=SYSTEM,
        temperature=0.1
    )

    return json.loads(result)["fixes"]
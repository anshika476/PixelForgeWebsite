# backend/app.py
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Correct agent imports
from agents.planner import plan_from_prompt
from agents.designer import generate_theme
from agents.codegen import generate_files
from agents.validator import validate_files

from services.file_manager import save_files_to_disk
from services.github_deployer import deploy_project

import uvicorn

app = FastAPI(title="AI Website Builder API")

# --------------------------
# CORS CONFIG
# --------------------------

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",  # Preview server
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# REQUEST MODEL
# --------------------------

class PromptIn(BaseModel):
    prompt: str


# --------------------------
# MAIN ENDPOINT
# --------------------------

@app.post("/generate")
async def generate_site(data: PromptIn):
    prompt = data.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    try:
        print("\n" + "="*70)
        print("STARTING WEBSITE GENERATION")
        print("="*70)
        print(f"Prompt: {prompt}")
        print()

        # 1️⃣ Planner → structure + metadata
        print("STEP 1: Planning...")
        plan = plan_from_prompt(prompt)
        print(f"✓ Plan created: {plan.get('site_title', 'Untitled')}")

        structure = plan.get("structure", plan)

        # 2️⃣ Designer → theme extraction
        print("\nSTEP 2: Designing...")
        design = generate_theme(prompt, plan)
        print(f"✓ Design created: {design.get('style', 'modern')}")

        # 3️⃣ Codegen → generate full project files
        print("\nSTEP 3: Generating code...")
        files = generate_files(prompt, structure, design)
        print(f"✓ Generated {len(files)} files")

        # 4️⃣ Validator → fix JSX if needed
        print("\nSTEP 4: Validating...")
        validated_files = validate_files(files)
        print(f"✓ Validated {len(validated_files)} files")


        print("\n" + "="*70)
        print("GENERATION COMPLETE")
        print("="*70 + "\n")

        project_name = plan.get(
            "site_title",
            "generated-site"
        )

        project_name = re.sub(
            r"[^a-zA-Z0-9-]",
            "-",
            project_name
        )

        project_name = project_name.lower().strip("-")

        project_path = save_files_to_disk(
            validated_files,
            project_name
        )

        deployment_url = deploy_project(
            project_path,
            project_name
        )

        return {
            "plan": plan,
            "design": design,
            "files": validated_files,
            "deployment": deployment_url
        }

    

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


# --------------------------
# HEALTH CHECK
# --------------------------

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "AI Website Builder API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# --------------------------
# RUN SERVER
# --------------------------

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
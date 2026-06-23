import uuid
import os

def save_files_to_disk(files, project_name):

    unique_id = str(uuid.uuid4())[:8]

    folder_name = f"{project_name}-{unique_id}"

    project_path = os.path.join(
        "generated_projects",
        folder_name
    )

    os.makedirs(project_path, exist_ok=True)

    for filepath, content in files.items():

        full_path = os.path.join(
            project_path,
            filepath
        )

        os.makedirs(
            os.path.dirname(full_path),
            exist_ok=True
        )

        with open(
            full_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(content)

    print(f"Project saved to: {project_path}")

    return project_path

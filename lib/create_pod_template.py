import runpod
import os
import json
from dotenv import load_dotenv
import requests
from pathlib import Path

load_dotenv()


API_KEY = os.getenv("RUNPOD_API_KEY")
runpod.api_key = API_KEY


def list_pod_templates():
    """
    List all available pod templates.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}

    query = {
        "query": """
        query getPodTemplates {
          myself {
            podTemplates {
              id
              name
              imageName
              category
              containerDiskInGb
              volumeInGb
              ports
              env { key value }
              readme
            }
          }
        }
      """
    }

    resp = requests.post("https://api.runpod.io/graphql", json=query, headers=headers)
    templates = resp.json()["data"]["myself"]["podTemplates"]
    # for t in templates:
    #    print(f"{t['id']:12} | {t['name']:<20} | {t['imageName']} | GPUs: {t['category']}")
    return templates


def delete_pod_template(template_id):
    """
    Delete a pod template by its ID.
    """
    resp = requests.delete(
        f"https://rest.runpod.io/v1/templates/{template_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )

    if resp.status_code == 204:
        print("Template deleted successfully ✅")
    else:
        print("Error deleting template:", resp.status_code, resp.text)


def create_pod_template(
    min_gb=24,
    name="comic-gen-template",
    image_name="runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
    container_disk_in_gb=10,
    volume_in_gb=10,
    volume_mount_path="/workspace",
):
    """
    Create a RunPod template for the comic generation task.
    """

    templates = list_pod_templates()
    for t in templates:
        if t["name"] == name:
            print(f"Template '{name}' already exists. Skipping creation.")
            return t["id"]

    tmpl = runpod.create_template(
        name=name,
        image_name=image_name,
        container_disk_in_gb=container_disk_in_gb,
        volume_in_gb=volume_in_gb,
        volume_mount_path=volume_mount_path,
        ports="8888/http,666/tcp",
    )
    print(f"Template created: {tmpl['id']}")
    print(json.dumps(tmpl, indent=2))

    template_dir = Path(__file__).parent.parent / "templates" / "pod_templates"
    template_dir.mkdir(exist_ok=True, parents=True)
    with open(template_dir / f"{name}.json", "w") as f:
        json.dump(tmpl, f, indent=4)
    print(f"Template saved to {template_dir / f'{name}.json'}")
    return tmpl


if __name__ == "__main__":
    # Example usage
    templates = list_pod_templates()
    if not templates:
        print("No pod templates found.")

    # Create a new template
    template_id = create_pod_template()
    print(template_id)
    delete_pod_template("3ecpsq3nw3")

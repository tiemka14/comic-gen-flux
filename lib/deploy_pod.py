import runpod
import os
import json
import time
from dotenv import load_dotenv
from lib.query_runpod_prices_types import get_min_price_gpu

load_dotenv()

runpod.api_key = os.getenv("RUNPOD_API_KEY")


def deploy_pod(
    template_id,
    image_name,
    gpu_count=1,
    volume_in_gb=100,
    container_disk_in_gb=100,
    name="ComicGenPod",
):
    """
    Deploy a pod using the specified template ID.
    """
    gpu_id = get_min_price_gpu(24)
    pod = runpod.create_pod(
        name=name,
        template_id=template_id,
        image_name=image_name,
        gpu_type_id=gpu_id,
        gpu_count=gpu_count,
        cloud_type="SECURE",
        volume_in_gb=volume_in_gb,
        container_disk_in_gb=container_disk_in_gb,
    )

    print(json.dumps(pod, indent=2))
    pod = runpod.get_pod(pod["id"])
    print(json.dumps(pod, indent=2))
    while pod["desiredStatus"] != "RUNNING":
        print("Waiting …", pod.status(), end="\r", flush=True)
        time.sleep(5)
        pod.refresh()
    return pod

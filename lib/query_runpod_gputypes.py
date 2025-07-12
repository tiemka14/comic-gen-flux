import runpod
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

runpod.api_key = os.getenv("RUNPOD_API_KEY")

pod_dict = runpod.get_gpus()
filtered_pod_dict = [gpu for gpu in pod_dict if gpu["memoryInGb"] >= 24]

pprint(filtered_pod_dict)

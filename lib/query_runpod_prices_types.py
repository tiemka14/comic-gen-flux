import os
import requests
import textwrap
from dotenv import load_dotenv

load_dotenv()


def get_min_price_gpu(min_gb):
    """
    Retrieves the ID of the cheapest available GPU from RunPod with at least the specified minimum VRAM (in GB).

    Args:
        min_gb (int): The minimum required GPU memory in gigabytes.

    Returns:
        str: The ID of the cheapest GPU that meets the memory requirement and is in stock.

    Side Effects:
        Prints the number of GPUs found that meet the criteria and details about the cheapest GPU.

    Raises:
        KeyError: If the expected keys are missing in the API response.
        ValueError: If no GPUs are found that meet the criteria.

    Note:
        Requires the environment variable 'RUNPOD_API_KEY' to be set for authentication.
    """
    url = "https://api.runpod.io/graphql"
    headers = {"Authorization": f"Bearer {os.getenv('RUNPOD_API_KEY')}"}

    query = """
    query PricesXGB($lp: GpuLowestPriceInput) {
      gpuTypes {                      
        id
        displayName
        memoryInGb
        lowestPrice(input: $lp) {
          uninterruptablePrice
          minimumBidPrice
          stockStatus
        }
      }
    }
    """

    vars = {
        "lp": {
            "gpuCount": 1,
            "minMemoryInGb": min_gb,
        }
    }

    resp = requests.post(
        url, json={"query": query, "variables": vars}, headers=headers
    ).json()

    filtered = [
        g
        for g in resp["data"]["gpuTypes"]
        if g["memoryInGb"]
        and g["memoryInGb"] >= min_gb
        and g["lowestPrice"]["stockStatus"] != "No-Stock"
        and g["lowestPrice"]["uninterruptablePrice"]
    ]

    print(
        textwrap.fill(
            f"Found {len(filtered)} GPUs with at least {min_gb} GB of VRAM available.",
            width=80,
        )
    )

    cheapest = min(filtered, key=lambda x: x["lowestPrice"]["uninterruptablePrice"])
    print(
        f"Cheapest GPU: {cheapest['displayName']} with {cheapest['memoryInGb']} GB VRAM at ${cheapest['lowestPrice']['uninterruptablePrice']:.2f} per hour (stock status: {cheapest['lowestPrice']['stockStatus']})."
    )

    return cheapest["id"]


if __name__ == "__main__":
    # Example usage: get_min_price_gpu(24) to find the cheapest GPU with at least 24 GB of VRAM.
    MIN_GB = 24

    cheapest = get_min_price_gpu(MIN_GB)
    print(f"Cheapest GPU ID: {cheapest}")

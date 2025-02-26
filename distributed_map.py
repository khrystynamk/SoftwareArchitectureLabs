import hazelcast
import os

from dotenv import load_dotenv

load_dotenv()

PORT1 = os.getenv("PORT1")
PORT2 = os.getenv("PORT2")
PORT3 = os.getenv("PORT3")


def create_distributed_map(filename: str):
    client = hazelcast.HazelcastClient(
        cluster_members=[
            PORT1,
            PORT2,
            PORT3,
        ]
    )

    distributed_map = client.get_map("randwords-distributed-map").blocking()

    with open(filename, "r") as file:
        words = [line.strip() for line in file.readlines()]

    if len(words) < 1001:
        raise ValueError("randwords.txt must contain at least 1001 words.")

    for i in range(1001):
        distributed_map.put(i, words[i])

    return distributed_map


if __name__ == "__main__":
    distributed_map = create_distributed_map("randwords.txt")
    sample_key = 500
    sample_value = distributed_map.get(sample_key)
    print(f"Sample Retrieved: {sample_key} -> {sample_value}")
    print("Total entries in map:", distributed_map.size())

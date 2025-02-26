import time
import threading
import hazelcast
import os

from dotenv import load_dotenv

load_dotenv()

PORT1 = os.getenv("PORT1")
PORT2 = os.getenv("PORT2")
PORT3 = os.getenv("PORT3")


def optimistic_locking():
    """
    In Hazelcast, you can apply the optimistic locking strategy with
    the map’s replace method. This method compares values in object or
    data forms depending on the in-memory format configuration.
    If the values are equal, it replaces the old value with the new one.
    """

    client = hazelcast.HazelcastClient(
        cluster_members=[
            PORT1,
            PORT2,
            PORT3,
        ]
    )

    map = client.get_map("map-optimistic-locking").blocking()
    key = "1"
    map.put_if_absent(key, 0)

    for _ in range(10000):
        while True:
            old_value = map.get(key)
            new_value = old_value + 1

            if map.replace_if_same(key, old_value, new_value):
                break

    client.shutdown()


def optimistic_locking_with_threads():
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=optimistic_locking)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    client = hazelcast.HazelcastClient(
        cluster_members=[
            PORT1,
            PORT2,
            PORT3,
        ]
    )
    map = client.get_map("map-optimistic-locking").blocking()

    final_value = map.get("1")
    print(f"Final value for 'key': {final_value}")
    client.shutdown()


if __name__ == "__main__":
    start = time.time()
    optimistic_locking_with_threads()
    end = time.time()
    print(f"Time taken for optimistic locking: {end - start} seconds")

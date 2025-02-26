import threading
import time
import hazelcast
import os

from dotenv import load_dotenv

load_dotenv()

PORT1 = os.getenv("PORT1")
PORT2 = os.getenv("PORT2")
PORT3 = os.getenv("PORT3")


class Value:
    def __init__(self):
        self.amount = 0


def pessimistic_locking():
    """
    One way to solve the race issue is by using pessimistic locking.
    It locks the map entry until you are finished with it.
    To perform pessimistic locking, use the lock mechanism provided
    by the Hazelcast distributed map, i.e., the map.lock and map.unlock methods.
    """

    client = hazelcast.HazelcastClient(
        cluster_members=[
            PORT1,
            PORT2,
            PORT3,
        ]
    )

    map = client.get_map("map-pessimistic-locking").blocking()
    key = "1"
    map.put_if_absent(key, Value())

    for _ in range(10000):
        map.lock(key)
        try:
            value = map.get(key)
            time.sleep(0.01)
            value.amount += 1
            map.put(key, value)
        finally:
            map.unlock(key)
    client.shutdown()


def pessimistic_locking_with_threads():
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=pessimistic_locking)
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
    map = client.get_map("map-pessimistic-locking").blocking()

    final_value = map.get("1")
    print(f"Final value for 'key': {final_value.amount}")
    client.shutdown()


if __name__ == "__main__":
    start = time.time()
    pessimistic_locking_with_threads()
    end = time.time()
    print(f"Time taken for pessimistic locking: {end - start} seconds")

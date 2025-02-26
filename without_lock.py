import hazelcast
import threading
import os

from dotenv import load_dotenv

load_dotenv()

PORT1 = os.getenv("PORT1")
PORT2 = os.getenv("PORT2")
PORT3 = os.getenv("PORT3")


def increment_value():
    client = hazelcast.HazelcastClient(
        cluster_members=[
            PORT1,
            PORT2,
            PORT3,
        ]
    )
    map = client.get_map("map-without-locks").blocking()
    map.put_if_absent("key", 0)

    for k in range(10000):
        value = map.get("key")
        value += 1
        map.put("key", value)

    client.shutdown()


def without_locks():
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=increment_value)
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
    map = client.get_map("map-without-locks").blocking()

    final_value = map.get("key")
    print(f"Final value for 'key': {final_value}")
    client.shutdown()


if __name__ == "__main__":
    without_locks()

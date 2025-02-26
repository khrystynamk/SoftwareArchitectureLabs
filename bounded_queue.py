import hazelcast
import threading
import os

from dotenv import load_dotenv

load_dotenv()

POISON_PILL = os.getenv("POISON_PILL", "-1")
QUEUE_NAME = os.getenv("QUEUE_NAME")
PORT1 = os.getenv("PORT1")
PORT2 = os.getenv("PORT2")
PORT3 = os.getenv("PORT3")


def produce(client, queue_name):
    queue = client.get_queue(queue_name).blocking()
    for i in range(1, 101):
        queue.put(i)
        print(f"Writing {i}")

    queue.put(POISON_PILL)


def consume(client, queue_name):
    queue = client.get_queue(queue_name).blocking()
    while True:
        value = queue.take()
        if value == POISON_PILL:
            break
        print(f"Consuming {value}")


def clients_wrapper():
    client = hazelcast.HazelcastClient(cluster_members=[PORT1, PORT2, PORT3])

    producer_thread = threading.Thread(target=produce, args=(client, QUEUE_NAME))
    consumer_thread1 = threading.Thread(target=consume, args=(client, QUEUE_NAME))
    consumer_thread2 = threading.Thread(target=consume, args=(client, QUEUE_NAME))

    producer_thread.start()
    consumer_thread1.start()
    consumer_thread2.start()

    producer_thread.join()
    consumer_thread1.join()
    consumer_thread2.join()

    queue = client.get_queue(QUEUE_NAME).blocking()
    queue.destroy()

    client.shutdown()


if __name__ == "__main__":
    clients_wrapper()

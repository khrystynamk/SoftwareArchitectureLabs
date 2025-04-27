# SoftwareArchitectureLabs - Consul

This repository features an improved microservices architecture that integrates a Hazelcast distributed map and Kafka message queues, all orchestrated with Consul for service discovery and configuration.

## 🐳 Launching Kafka with Docker

To launch Kafka with Docker, create a `docker-compose.yml` file configured to run **3 Kafka brokers**.

### Commands:
```bash
docker-compose up -d
docker pull apache/kafka
docker pull hashicorp/consul
```

![Compose](./img/docker-compose.png)
![Docker](./img/docker-run.png)

```bash
docker exec -it broker-1 /opt/kafka/bin/kafka-topics.sh --create \
  --bootstrap-server broker-1:19092,broker-2:19092,broker-3:19092 \
  --replication-factor 3 \
  --partitions 1 \
  --topic messages
```

## Starting all services

Use the included startup script to launch everything:
**Note**: Make sure the ```hazelcast-5.5.0``` directory is in the same workspace.

```bash
./start_services.sh
```

This script starts the following services:
- `facade-service`
- **three instances** of `logging-service`, each instance has its own **Hazelcast** node.
- **two instances** of `messages-service`.

## Registering All Services

After registering all services, the following steps and results are achieved:

- **Kafka MessageQueue and Hazelcast Key-Value Pairs**

  ![Added](./img/added-kvs.png)

- **Service Registration Overview**

  ![Registeres](./img/registered-1.png)

  ![Registeres](./img/registered-2.png)

Once the services are registered, they can be discovered via Consul. This enables other services to locate and connect to them easily.

  ![Services](./img/services.png)

  ![Messages](./img/messages.png)

  ![Logging](./img/logging.png)

After registering the services, the system also manages key-value data in Kafka and Hazelcast. This allows for efficient data exchange and persistence across the system.

- **Kafka Key-Value Pair Storage**

  ![KV](./img/kafka-kv.png)

- **Hazelcast Key-Value Pair Storage**

  ![KV](./img/hazelcast-kv.png)

## GET and POST requests

Below are the results demonstrating successful **POST** and **GET** request handling:

**POST Request:**
- Message sent
- Message added to the queue

![POST](./img/post_message.png)
![POST](./img/post_message_queue.png)

**GET Request:**
- Message retrieval
- Retrieved message result

![GET](./img/get_message.png)
![GET](./img/get_message_result.png)

## Disabling a Service

I manually disabled the **Logging service (instance 1)** using `lsof` and `kill` commands.  
After termination, the service was automatically **deregistered from the Consul UI**.  
Despite this, **GET** requests continued to function as intended.

![Killed](./img/kill_service.png)
![Consul Stopped](./img/consul_service_stopped.png)
![GET Stopped](./img/get_service_stopped.png)

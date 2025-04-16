# SoftwareArchitectureLabs

This repository contains an improved implementation of a basic microservices architecture with an incorporated Hazelcast distributed map.

---

## Tasks and Results

### 1. Start Three Instances of Logging-Service (with Three Hazelcast Nodes)

You can start the system using the `bash` script, specifically `start_services.sh`. But before that you might need to add the `hazelcast-5.5.0` folder to workspace.

```
./start_services.sh
```

The system initializes three instances of the logging service, each running on a separate Hazelcast node.

#### Nodes:
![Nodes](img/nodes.png)

#### Logging Services:
![Logging services](img/logging.png)

---

### 2. Write 10 Messages via `facade-service` Using HTTP POST

Messages are distributed across the three logging service instances:

- **Instance 0**: 2 messages
- **Instance 1**: 5 messages
- **Instance 2**: 3 messages

#### Post Result:
![Post result](img/msgs_added.png)

---

### 3. Retrieve Messages via `facade-service` Using HTTP GET

All messages are successfully retrieved from the Hazelcast distributed map.

#### Get Result:
![Get result](img/get_result.png)

---

### 4. Shutdown One/Two Instances of Logging Service (With Hazelcast Nodes) and Verify Data Availability

Even after shutting down two logging service instances along with their corresponding nodes, all messages remain accessible in the distributed map.
The processes were killed using the following command

```bash
pkill -f <process_name_attr>
```

For example:

```bash
pkill -f "java .*hazelcast.*5701"
pkill -f "java .*hazelcast.*5702"

pkill -f "uvicorn logging_service:app --host 127.0.0.1 --port 8081"
pkill -f "uvicorn logging_service:app --host 127.0.0.1 --port 8082"
```

#### Logs After Shutdown:
![Logs with shutdown](img/two_services_shutdown.png)

#### Get Result After Shutdown:
![Result with shutdown](img/get_result_shutdown.png)

---

## Additional Implemented Features

- **Config Server**  
  Configuration requests are logged and can be observed in the log images above.

  ![Config Server Request](img/config_server_request.png)

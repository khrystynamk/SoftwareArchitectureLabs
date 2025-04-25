import consul


def register_service(service_name, service_id, port, address):
    consul_service = consul.Consul(host="localhost", port=8500)
    consul_service.agent.service.register(
        name=service_name,
        service_id=str(service_name) + "-" + str(service_id),
        address=address,
        port=int(port),
    )
    print(
        f"Registered with Consul\nService: {service_name}\nService ID: {service_id}\nAddress: {address}:{port}"
    )


def deregister_service(service_id):
    consul_service = consul.Consul()
    consul_service.agent.service.deregister(str(service_id))
    print(f"Deregistered with Consul\nService ID: {service_id}")


def discover_service(service_name):
    consul_service = consul.Consul(host="localhost", port=8500)
    _, services = consul_service.health.service(service_name, passing=True)
    return [
        f"http://{service['Service']['Address']}:{service['Service']['Port']}"
        for service in services
    ]


def add_key_value_item(key, value):
    consul_service = consul.Consul(host="localhost", port=8500)
    consul_service.kv.put(key, value)
    print(f"Added key-value item: {key} = {value}")


def get_key_value_item(key):
    consul_service = consul.Consul(host="localhost", port=8500)
    _, value = consul_service.kv.get(key)
    if value:
        print(f"Retrieved key-value item: {key} = {value['Value']}")
        return value["Value"]
    else:
        print(f"Key {key} not found")
        return None


if __name__ == "__main__":
    add_key_value_item("kafka/topic", "messages")
    add_key_value_item("kafka/nodes", "localhost:29092,localhost:39092,localhost:49092")
    add_key_value_item(
        "hazelcast/nodes", "127.0.0.1:5701,127.0.0.1:5702,127.0.0.1:5703"
    )
    add_key_value_item("hazelcast/cluster_name", "dev")

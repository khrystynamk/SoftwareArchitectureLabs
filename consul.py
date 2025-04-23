import consul


def register_service(service_name, service_id, port, address):
    consul_service = consul.Consul(host="localhost", port=8500)
    consul_service.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=address,
        port=port,
    )
    print(
        f"Registered with Consul\nService: {service_name}\nService ID: {service_id}\nAddress: {address}:{port}"
    )


def deregister_service(service_id):
    consul = consul.Consul()
    consul.agent.service.deregister(service_id)
    print(f"Deregistered with Consul\nService ID: {service_id}")


def discover_service(service_name):
    consul_service = consul.Consul(host="consul", port=8500)
    _, services = consul_service.health.service(service_name, passing=True)
    return [
        f"http://{service['Service']['Address']}:{service['Service']['Port']}"
        for service in services
    ]

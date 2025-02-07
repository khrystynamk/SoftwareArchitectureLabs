import grpc
import facade_logging_service_pb2_grpc
import facade_logging_service_pb2
import uuid

from concurrent import futures

added_messages = {}


class LoggingServiceServicer(facade_logging_service_pb2_grpc.LoggingServicer):
    def PutMessage(self, request, context):
        if request.text in added_messages.values():
            added_uuid = added_messages.get(request.text, None)
            return facade_logging_service_pb2.PutMessageResponse(
                status=403, uuid=added_uuid, text="message has been already added"
            )

        message_uuid = str(uuid.uuid4())
        added_messages[message_uuid] = request.text
        return facade_logging_service_pb2.PutMessageResponse(
            status=200, uuid=message_uuid, text=request.text
        )

    def GetMessages(self, request, context):
        return facade_logging_service_pb2.GetMessagesResponse(
            messages=added_messages.values()
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    facade_logging_service_pb2_grpc.add_LoggingServicer_to_server(
        LoggingServiceServicer(), server
    )
    server.add_insecure_port("localhost:8081")
    print("Logging Service is running on port 8081...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

import grpc
import os
import facade_logging_service_pb2_grpc
import facade_logging_service_pb2

from concurrent import futures
from dotenv import load_dotenv

added_messages = {}
load_dotenv("../.env")
CHANNEL = os.getenv("CHANNEL")


class LoggingServiceServicer(facade_logging_service_pb2_grpc.LoggingServicer):
    def LogMessage(self, request, context):
        if request.uuid in added_messages.keys():
            return facade_logging_service_pb2.LogMessageResponse(
                status=400, uuid=request.uuid, text="message has been already added"
            )

        added_messages[request.uuid] = request.text
        return facade_logging_service_pb2.LogMessageResponse(status=200)

    def GetMessages(self, request, context):
        return facade_logging_service_pb2.GetMessagesResponse(
            messages=list(added_messages.values())
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    facade_logging_service_pb2_grpc.add_LoggingServicer_to_server(
        LoggingServiceServicer(), server
    )
    server.add_insecure_port(CHANNEL)
    print("Logging Service is running on port 8081...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

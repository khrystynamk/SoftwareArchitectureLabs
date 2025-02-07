import uuid
from pydantic import BaseModel


class Message(BaseModel):
    text: str
    mes_uuid: uuid.UUID = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.mes_uuid is None:
            self.mes_uuid = uuid.uuid4()

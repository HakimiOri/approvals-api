from pydantic import BaseModel

class ApprovalsRequest(BaseModel):
    addresses: list[str]


from pydantic import BaseModel


class HealthData(BaseModel):
    status: str


class HealthResponse(BaseModel):
    data: HealthData

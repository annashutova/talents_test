from typing import List

from pydantic import BaseModel


class TraitObject(BaseModel):
    id: int
    trait_lack: str
    trait_virtue: str
    trait_excess: str

    class Config:
        from_attributes = True


class TraitsResponse(BaseModel):
    traits: List[TraitObject]

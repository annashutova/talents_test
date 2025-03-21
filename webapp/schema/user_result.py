from typing import List

from pydantic import BaseModel


class TraitDegreeInterpretationSchema(BaseModel):
    title: str
    coefficient: float
    short_description: str
    long_description: str


class ResultInterpretationSchema(BaseModel):
    trait_id: int
    trait_lack: TraitDegreeInterpretationSchema
    trait_virtue: TraitDegreeInterpretationSchema
    trait_excess: TraitDegreeInterpretationSchema


class ResultInterpretationResponse(BaseModel):
    traits: List[ResultInterpretationSchema]

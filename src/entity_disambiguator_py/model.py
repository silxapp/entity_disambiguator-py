from typing import Optional
from pydantic import BaseModel


class UMLSAtom(BaseModel):
    atom_id: str
    concept_id: str
    name: str


class UMLSConcept(BaseModel):
    concept_id: str
    language: str
    alias_list: list[str]
    definition: Optional[str]


class MessageResponse(BaseModel):
    message: str


class GetAliasesResponse(BaseModel):
    id: int
    result: list[UMLSAtom]


class GetConceptResponse(BaseModel):
    id: int
    result: UMLSConcept


class ListConceptResponse(BaseModel):
    id: int
    result: list[str]

from enum import Enum
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


class UMLSRelationship(BaseModel):
    parent: str
    child: str
    rel_type: str
    umls_primary: Optional[str]
    umls_secondary: Optional[str]


class GetNeighborsResponse(BaseModel):
    id: int
    result: list[UMLSRelationship]


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


class GetConceptInfoResponse(BaseModel):
    concept_id: str
    definition: str
    alias_names: list[str]


class RelationshipType(Enum):
    SYN = 1
    PRED = 2
    CAUS = 3
    MOD = 4
    COMP = 5
    DEL = 6
    TREATS = 7
    MEASURES = 8
    ASSOC = 9
    CONTR = 10
    TRANS = 11


class Relationship(BaseModel):
    parent: str
    child: str


class GraphTraversalResponse(BaseModel):
    id: int
    edges: list[Relationship]

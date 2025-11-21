from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UMLSAtom(BaseModel):
    atom_id: str
    concept_id: str
    name: str
    source: str


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


class GetFamilyResponse(BaseModel):
    id: int
    edges: list[UMLSRelationship]


class MessageResponse(BaseModel):
    message: str


class GetAliasResponse(BaseModel):
    id: int
    result: UMLSAtom


class BatchGetAliasResponse(BaseModel):
    id: int
    result: list[UMLSAtom]


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


class DocDBRelationship(BaseModel):
    parent: str
    child: str
    rel_type: str
    umls_primary: Optional[str]
    umls_secondary: Optional[str]


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


class CanonicalSynonym(BaseModel):
    cui_id: str
    canonical_cui: str
    synset_id: str


class CanonicalSynonymsResponse(BaseModel):
    id: int
    result: CanonicalSynonym


class SynonymSet(BaseModel):
    synset_id: str
    subgraph: list[str]


class SynonymSetResponse(BaseModel):
    id: int
    result: SynonymSet

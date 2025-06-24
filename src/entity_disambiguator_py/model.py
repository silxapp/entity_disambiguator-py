from pydantic import BaseModel

class UMLSAtom(BaseModel):
    atom_id: str
    concept_id: str
    name: str


class MessageResponse(BaseModel):
    message: str


class GetAliasesResponse(BaseModel):
    id: int
    result: list[UMLSAtom]

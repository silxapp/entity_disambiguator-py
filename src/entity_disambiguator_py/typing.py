from typing import Protocol, runtime_checkable

from entity_disambiguator_py.model import (
    BatchGetAliasNameResponse,
    BatchGetAliasResponse,
    BatchGetConceptResponse,
    CanonicalSynonymsResponse,
    GetAliasNameResponse,
    GetAliasResponse,
    GetConceptResponse,
    GetNeighborsResponse,
    GetTypeDefinitionResponse,
    GraphTraversalResponse,
    SynonymSetResponse,
)


@runtime_checkable
class UMLSGraphInterface(Protocol):
    def get_parents(self, umls_id: str, sort_prefix: str) -> GetNeighborsResponse: ...
    def get_children(self, umls_id: str, sort_prefix: str) -> GetNeighborsResponse: ...
    def get_neighbors(self, umls_id: str, sort_prefix: str) -> GetNeighborsResponse: ...
    def get_ancestors(
        self, umls_id: str, sort_prefix: str, depth_limit: int
    ) -> GraphTraversalResponse: ...
    def get_descendants(
        self, umls_id: str, sort_prefix: str, depth_limit: int
    ) -> GraphTraversalResponse: ...
    def get_subgraph(
        self, umls_id: str, sort_prefix: str, depth_limit: int
    ) -> GraphTraversalResponse: ...


@runtime_checkable
class UMLSVocabularyInterface(Protocol):
    def get_alias_id(self, alias_id: str) -> GetAliasResponse: ...
    def get_batch_alias_id(self, alias_ids: list[str]) -> BatchGetAliasResponse: ...
    def get_alias_name(self, name: str) -> GetAliasNameResponse: ...
    def get_batch_alias_name(self, names: list[str]) -> BatchGetAliasNameResponse: ...
    def get_concept(self, concept_id: str) -> GetConceptResponse: ...
    def get_type_definition(self, tui: str) -> GetTypeDefinitionResponse: ...
    def get_batch_concept(self, concept_ids: list[str]) -> BatchGetConceptResponse: ...


@runtime_checkable
class UMLSSynonymInterface(Protocol):
    def get_synonym_set(self, ssid: str) -> SynonymSetResponse: ...
    def get_canonical_synonyms(self, cid: str) -> CanonicalSynonymsResponse: ...


@runtime_checkable
class UMLSDbInterface(
    UMLSGraphInterface, UMLSVocabularyInterface, UMLSSynonymInterface, Protocol
): ...

from typing import List, Optional
from pydantic import BaseModel, Field

class ConceptNode(BaseModel):
    id: str
    label: str
    summary: str
    embedding: Optional[List[float]] = None
    children: List['ConceptNode'] = Field(default_factory=list)

# Enable recursion for ConceptNode
ConceptNode.model_rebuild()

class PaperSchema(BaseModel):
    title: str
    root_concept: ConceptNode

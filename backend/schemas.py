# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import List


class Component(BaseModel):
    name: str
    technology: str


class DataFlow(BaseModel):
    source: str
    destination: str
    description: str


class SystemDescription(BaseModel):
    components: List[Component]
    data_flows: List[DataFlow]
    trust_boundaries: List[str]
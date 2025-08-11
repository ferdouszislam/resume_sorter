from dataclasses import dataclass


@dataclass
class ResumeRetrieverAgentDependency:
    rag_table_name: str
    limit: int
    reranker_weight: float

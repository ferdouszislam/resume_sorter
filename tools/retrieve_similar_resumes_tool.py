import os
from pydantic_ai import RunContext
from models.resume_retriever_agent_dependency import ResumeRetrieverAgentDependency
from models.resume import Resume
from typing import List
from helpers import rag_db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# read environment vars
RELEVANCE_SCORE_THRESHOLD = float(os.environ.get("RELEVANCE_SCORE_THRESHOLD"))


def retrieve_relevant_resumes(ctx: RunContext[ResumeRetrieverAgentDependency], query: str) -> List[Resume]:
    """
        Retrieve and convert relevant resumes from the database based on a search query.

        This tool function performs semantic search through a collection of resumes and
        converts the raw document results into structured Resume objects. It handles both
        formal job descriptions and casual search queries, returning candidates ranked by
        relevance to the search criteria.

        Args:
            ctx: the context
            query: Search query describing the desired candidate profile. Examples:
                - "Senior Python developer with machine learning experience"
                - "Marketing manager with startup background"
                - "Full-stack engineer React Node.js 5 years"

        Returns:
            List[Resume]: List of Resume objects containing candidate information. Each
                Resume object has:
                - label: Identifier or name for the resume
                - content: Full text content of the resume
                Results are ordered by relevance score (highest first).
    """
    print('retrieve_relevant_resumes tool invoked')
    resume_retriever_agent_deps: ResumeRetrieverAgentDependency = ctx.deps
    retrieved_docs: List[dict] = rag_db.retrieve_similar_docs(
        query=query,
        table_name=resume_retriever_agent_deps.rag_table_name,
        limit=resume_retriever_agent_deps.limit,
        reranker_weight=resume_retriever_agent_deps.reranker_weight)
    retrieved_docs = [doc for doc in retrieved_docs if doc.get('_relevance_score', 0) > RELEVANCE_SCORE_THRESHOLD]
    retrieved_resumes: List[Resume] = []
    for retrieved_doc in retrieved_docs:
        retrieved_resume = Resume(label=retrieved_doc['label'], content=retrieved_doc['text'],
                                  relevance_score=retrieved_doc['_relevance_score'])
        retrieved_resumes.append(retrieved_resume)
    print(f'retrieved {len(retrieved_resumes)} resumes: {[r.label for r in retrieved_resumes]}')
    return retrieved_resumes

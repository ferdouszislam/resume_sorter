from pydantic import BaseModel, Field


class Resume(BaseModel):
    """
    Contains information of a resume.
    """
    label: str = Field(description="Contains the label used to identify this resume.")
    content: str = Field(description="Content of the entire resume.")
    relevance_score: float = Field(description=
                                   "Higher value means the resume is more relevant to the query. "
                                   "To be used in sorting retrieved resumes but never expose to user", ge=0, le=1)

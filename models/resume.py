from pydantic import BaseModel, Field


class Resume(BaseModel):
    """
    Contains minimal information of coworkers employee record.
    """
    label: str = Field(description="Contains the label used to identify this resume.")
    content: str = Field(description="Content of the entire resume.")

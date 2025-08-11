import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.openai import OpenAIProvider
from tools.retrieve_similar_resumes_tool import retrieve_relevant_resumes
from models.resume_retriever_agent_dependency import ResumeRetrieverAgentDependency

# read environment vars
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
MODEL = os.environ.get('MODEL')


# read instructions from file
def load_instructions(file_path='llm_instructions.md'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


# initialize model
if MODEL == 'gemini':
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=GOOGLE_API_KEY))
elif MODEL == 'openai':
    model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(api_key=OPENAI_API_KEY))
else:
    ValueError(f'invalid model name: {MODEL}')

# initialize agent
resume_sorter_agent = Agent(model=model,
                            instructions=load_instructions(),
                            deps_type=ResumeRetrieverAgentDependency,
                            retries=3,
                            tools=[retrieve_relevant_resumes],)

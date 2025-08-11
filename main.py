from agent import resume_sorter_agent
from models.resume_retriever_agent_dependency import ResumeRetrieverAgentDependency
import rag_db

# initialize agent dependency
resume_retriever_agent_deps = ResumeRetrieverAgentDependency(
    rag_table_name=rag_db.TABLE_NAME, limit=10, reranker_weight=0.7, relevance_score_threshold=0.7)

message_history = []
while True:
    query = input('>: ')
    if query == 'exit':
        break
    response = resume_sorter_agent.run_sync(
        user_prompt=query,
        deps=resume_retriever_agent_deps,
        message_history=message_history)
    print(f'>>{response.output}')
    message_history.extend(response.new_messages())
    message_history = message_history[-5:]
    print('==================================llm-usage==================================')
    usage = response.usage()
    print(f'requests: {usage.requests}, '
          f'request_tokens: {usage.request_tokens}, '
          f'response_tokens": {usage.response_tokens}')
    print('=============================================================================')

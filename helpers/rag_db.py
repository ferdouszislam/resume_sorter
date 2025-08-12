import os
from pathlib import Path
import tiktoken
import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from lancedb.table import LanceTable
from lancedb.rerankers import RRFReranker, CrossEncoderReranker, LinearCombinationReranker, CohereReranker
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# read environment vars
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
DB_PATH = os.environ.get('DB_PATH')
TABLE_NAME = os.environ.get('TABLE_NAME')
RESUME_DIR = os.environ.get('RESUME_DIR')
MODEL = os.environ.get('MODEL')

# initialize embedding model
registry = get_registry()
if MODEL == 'gemini':
    registry.set_var("api_key", GOOGLE_API_KEY)
    embeddings = registry.get('gemini-text').create()
elif MODEL == 'openai':
    registry.set_var("api_key", OPENAI_API_KEY)
    embeddings = registry.get('openai').create(name='text-embedding-ada-002')
else:
    ValueError(f'invalid model: {MODEL}')


class Document(LanceModel):
    """
    Define the schema for documents to be stored in LanceDB table
    """
    id: str
    label: str
    file_name: str
    text: str = embeddings.SourceField()
    vector: Vector(embeddings.ndims()) = embeddings.VectorField()


def chunk_text(text: str, max_tokens: int = 8192, encoding_name: str = 'cl100k_base'):
    """
    Chunk text to smaller parts to fit within a maximum token limit
    """
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    for i in range(0, len(tokens), max_tokens):
        yield encoding.decode(tokens[i: i + max_tokens])


def create_lancedb_table(db_path: str, table_name: str, overwrite: bool = True):
    """
    Connect to Lancedb and create a table for storing knowledge documents.
    """
    db = lancedb.connect(db_path)
    mode = 'overwrite' if overwrite else 'create'
    table = db.create_table(table_name, schema=Document, mode=mode)
    table.create_fts_index('text', replace=overwrite)
    return table


def drop_lancedb_table(db_path: str = DB_PATH, table_name: str = TABLE_NAME):
    """
    Drop a Lancedb table if it exists.
    """
    db = lancedb.connect(db_path)
    db.drop_table(table_name)


def add_docs_to_knowledge_base(table: LanceTable, knowledge_base_dir: str,
                               doc_file_ext: str = '.md', max_tokens: int = 8192):
    """
    Add documents to knowledge base
    """
    docs = []
    knowledge_base = Path(knowledge_base_dir)
    for md_file in knowledge_base.glob(f'*{doc_file_ext}'):
        print(f'processing {md_file.name}')
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
            doc_label = md_file.stem
            doc_id = f'{doc_label}_{time.time()}'
            doc_file_name = md_file.name
            doc = {'id': doc_id, 'label': doc_label, 'file_name': doc_file_name, 'text': text}
            docs.append(doc)
            print(f'adding doc- {doc_id}')
            # for i, chunk in enumerate(chunk_text(text, max_tokens=max_tokens)):
            #     doc_label = md_file.stem
            #     doc_id = f'{doc_label}_{i}'
            #     doc_file_name = md_file.name
            #     doc = {'id': doc_id, 'label': doc_label, 'file_name': doc_file_name, 'text': chunk}
            #     docs.append(doc)
            #     print(f'adding doc- {doc_id}')
    if docs:
        table.add(docs)
    else:
        print('no doc found/added')


def setup_lancedb():
    """
    Set up LanceDB with initial configuration
    """
    print('setting up lancedb')
    table = create_lancedb_table(db_path=DB_PATH, table_name=TABLE_NAME, overwrite=True)
    add_docs_to_knowledge_base(table, knowledge_base_dir=RESUME_DIR)
    return table


def get_table(table_name: str = TABLE_NAME):
    db = lancedb.connect(DB_PATH)
    return db.open_table(table_name) if db.table_names() else setup_lancedb()


def get_row_by(field_name, field_value, table_name=TABLE_NAME):
    table = get_table(table_name)
    try:
        # Use where clause to filter by ID
        result = table.search().where(f"{field_name} = '{field_value}'").limit(5).to_list()
        print(len(result))
        print(r['id'] for r in result)
        return result[0] if result else None
    except Exception as e:
        print(f"Error searching for {field_name} {field_value}: {e}")
        return None


def get_all_rows(table_name: str = TABLE_NAME):
    table = get_table(table_name)
    try:
        df = table.to_pandas()
        results = df.to_dict('records')  # Convert to list of dicts
        return results
    except Exception as e:
        print(f"Error fetching rows: {e}")
        return []


def retrieve_similar_docs(query: str, table_name: str = TABLE_NAME, limit: int = 20, reranker_weight: float = 0.3):
    """
    Retrieve docs from the LanceDB table then rerank them
    """
    table = get_table(table_name=table_name)
    # hybrid search
    reranker = LinearCombinationReranker(weight=reranker_weight)
    results = (
        table.search(query, query_type='hybrid').rerank(reranker=reranker).limit(limit).to_list()
    )

    print(f'fetched {len(results)} resumes.')
    for r in results:
        print(f'{r["label"]} ({r["_relevance_score"]})')
    return results

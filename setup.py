import pdf_to_md
import rag_db

# pdf_to_md.convert_pdfs_to_md(pdf_dir="./resumes", output_dir="./resumes_in_md")
rag_db.drop_lancedb_table()
rag_db.setup_lancedb()

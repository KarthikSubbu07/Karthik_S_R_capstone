## MP2 - RAG
The mp2_rag.py file is designed to ingest / ask / evaluate the provided corpus using qdrant as the vector database.
Ensure the env file [created in your local or env] has the openai_api_key, qdrant_api_key and qdrant_url

There are 3 major modules
Ingest :cmd_ingest() method is used to chunk [by paragraphs - section], embed and store the vectors in qdrant
ask: cmd_ask() method is used to retrieve topk snippets and provide an LLm generated answer for a given user Q
validate: cmd_validate() is used to validate predefined and learner_defined questions.

Pls run the "mp2_rag.py" file using python mp2_rag.py + one of the 3 commands to either ingest, ask or validate the pipeline.

Ensure the user defined questions are present in W9_MP2/data/predefined_questions.jsonl
install the requirements before running the script
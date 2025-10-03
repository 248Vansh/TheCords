# pathwayPipeline.py
import pathway as pw
from pathway import this
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.parsers import UnstructuredParser
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.xpacks.llm import embedders
from pathway.stdlib.indexing.nearest_neighbors import BruteForceKnnFactory
from dotenv import load_dotenv
import os
from google import genai

# Load Gemini API key
load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1️⃣ Load PDFs from the 'highways' folder
documents = pw.io.fs.read("./highways/", format="binary", with_metadata=True)

# 2️⃣ Prepare components for document store
text_splitter = TokenCountSplitter(
    min_tokens=100,
    max_tokens=500,
    encoding_name="cl100k_base"
)

parser = UnstructuredParser(
    chunking_mode="by_title",
    chunking_kwargs={"max_characters": 3000, "new_after_n_chars": 2000}
)

# 3️⃣ Use GeminiEmbedder for embeddings
embedder = embedders.GeminiEmbedder(model="models/text-embedding-004")

# 4️⃣ Create the Document Store with BruteForceKnnFactory
document_store = DocumentStore(
    docs=documents,
    retriever_factory=BruteForceKnnFactory(embedder=embedder),
    parser=parser,
    splitter=text_splitter
)

# 5️⃣ Function to query the document store
def get_relevant_docs(query, k=3):
    """
    Returns top-k relevant documents from highways PDFs based on query
    """
    # Create a table with proper types
    t = pw.debug.table_from_markdown('''
filepath_globpattern  metadata_filter  k  query
./highways/*           None             0  dummy
''')

    # Set actual values
    t = t.select(
        filepath_globpattern="./highways/*",
        metadata_filter=None,   # Must be None, not {}
        k=int(k),
        query=query
    )

    retrieved = document_store.retrieve_query(
        retrieval_queries=t.select(
            filepath_globpattern=this.filepath_globpattern,
            metadata_filter=this.metadata_filter,
            k=this.k,
            query=this.query
        )
    )

    retrieved = retrieved.select(docs=this.result)
    return retrieved

from google import genai
import os
from dotenv import load_dotenv
from weather import get_weather

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def answer_query(query, cities=None, k=3):
    """
    Generate an answer using Gemini LLM.
    Uses Pathway document_store to retrieve relevant context.
    Optionally, provide a list of cities to fetch live weather and include in the prompt.
    """
    # 🔎 Step 1: Retrieve relevant docs from Pathway
    retrieved_docs = get_relevant_docs(query, k=k).to_pandas()
    context_docs = "\n\n".join([str(doc) for doc in retrieved_docs["docs"].tolist()])

    # 🌦 Step 2: Add optional weather info
    context_weather = ""
    if cities:
        weather_info = []
        for city in cities:
            desc, temp = get_weather(city)
            weather_info.append(f"{city}: {desc}, {temp}°C")
        context_weather = "Live weather along the route:\n" + "\n".join(weather_info)

    # 📝 Step 3: Build the final prompt
    prompt = f"""
You are a travel assistant. Use the following context from highway PDFs to answer:

Context:
{context_docs}

User query: {query}

{context_weather if context_weather else ""}
Provide a short, practical, easy-to-read response. Use emojis where relevant.
"""
    # 🤖 Step 4: Call Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text








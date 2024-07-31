import os
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

if gemini_api_key is None:
    print("GEMINI_API_KEY is not set")
else:
    os.environ['GEMINI_API_KEY'] = gemini_api_key
    print(f"GEMINI_API_KEY is set")


from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.gemini import Gemini


documents = SimpleDirectoryReader("data").load_data()



from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# Set up Gemini LLM
llm = Gemini(
    model="models/gemini-1.5-flash",
    api_key=gemini_api_key
)

# Set up Gemini Embedding model
embed_model = GeminiEmbedding(
    model_name="models/embedding-001",
    api_key=gemini_api_key)



from llama_index.core import ServiceContext, Settings, VectorStoreIndex

# Configure settings
Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = 1024

# Create service context
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)



# Create index
index = VectorStoreIndex.from_documents(
    documents, 
    service_context=service_context,
    show_progress=True
)



from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)



query_engine = index.as_query_engine()



chat_history  = []



def ask_question(query):
    # Combine previous chat history for context
    context = "\n".join([f"Q: {q['query']}\nA: {q['response']}" for q in chat_history])
    full_query = f"{context}\n\nQ: {query}"
    
    # Perform the query
    response = query_engine.query(full_query)
    
    # Store the chat history
    chat_history.append({
        "query": query,
        "response": str(response)
    })
    
    return response


response = ask_question("how did Anya figure out that the images depicted a timeline of the civilization on Proxima Centauri b?")
print(response)


response = ask_question("Can you reframe what you just said?")
print(response)
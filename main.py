import os
from dotenv import load_dotenv
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.gemini import Gemini
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import ServiceContext, Settings, VectorStoreIndex


load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

if gemini_api_key is None:
    st.error("GEMINI_API_KEY is not set")
    st.stop()
else:
    os.environ['GEMINI_API_KEY'] = gemini_api_key



# Set up Gemini LLM
llm = Gemini(
    model="models/gemini-1.5-flash",
    api_key=gemini_api_key
)

# Set up Gemini Embedding model
embed_model = GeminiEmbedding(
    model_name="models/embedding-001",
    api_key=gemini_api_key)


# Configure settings
Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = 1024


# Create service context
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)



# Load documents and create index
@st.cache_resource
def load_data():
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    return index




# Create index
index = load_data()



# query engine
query_engine = index.as_query_engine()



# Chat history and ask_question function
chat_history = []

# Function to generate response
def generate_response(prompt, chat_history):
    # Combine chat history for context
    context = "\n".join([f"Human: {q}" + (f"\nAssistant: {a}" if a else "") for q, a in chat_history])
    full_query = f"{context}\nHuman: {prompt}\nAssistant:"
    
    # Generate response
    response = query_engine.query(full_query)
    return str(response)

# Streamlit UI
st.title("Chat with your docs")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = generate_response(prompt, [(m["content"], m.get("response", "")) for m in st.session_state.messages])
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a button to clear the conversation
if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
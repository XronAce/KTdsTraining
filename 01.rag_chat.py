import os

from dotenv import load_dotenv
from openai import AzureOpenAI
import streamlit as st

os.system('cls' if os.name == 'nt' else 'clear')
load_dotenv(override=True)

# Get environment variables
openai_endpoint = os.getenv("OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai_api_key = os.getenv("OPENAI_API_KEY")
chat_model = os.getenv("CHAT_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_api_key = os.getenv("SEARCH_API_KEY")
index_name = os.getenv("INDEX_NAME")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=openai_endpoint,
    api_key=openai_api_key,
    api_version=api_version
)


def get_openai_response(messages):
    rag_params = {
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": index_name,
                    "authentication": {
                        "type": "api_key",
                        "key": search_api_key,
                    },
                    "query_type": "vector",
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": embedding_model,
                    }
                }
            }
        ],
    }

    openai_response = client.chat.completions.create(
        model=chat_model,
        messages=messages,
        extra_body=rag_params
    )

    return openai_response.choices[0].message.content


st.title("Margie's Travel Assistant")

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a travel assistant that provides information on travel service available from Margie's Travel."
        }
    ]

for message in st.session_state.messages:
    if message['role'] != 'system':
        st.chat_message(message['role']).write(message['content'])

if user_input := st.chat_input("Enter your question: "):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.spinner("응답을 기다리는 중..."):
        response = get_openai_response(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

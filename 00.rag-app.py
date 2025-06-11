import os
from dotenv import load_dotenv
from openai import AzureOpenAI


def main():
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

  #Initialize Azure OpenAI client
  client = AzureOpenAI(
      azure_endpoint=openai_endpoint,
      api_key=openai_api_key,
      api_version=api_version
  )

  # Initialize prompt with system message
  prompt = [
    {
      "role": "system",
      "content": "You are a travel assistant that provides information on travel service available from Margie's Travel."
    }
  ]
  print(f"DEBUG - search_endpoint: [{search_endpoint}]")


  while True:
    input_text = input("Enter your question (or 'exit' to quit): ")
    if input_text.lower() == 'exit':
      print("Exiting the application.")
      break
    elif input_text.strip() == "":
      print("Please enter a valid question.")
      continue

    # Add user input to the prompt
    prompt.append({"role": "user", "content": input_text})

    # Additional parameters to apply RAG pattern using the AI Search index
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

    # Call the Azure OpenAI chat completion API
    response = client.chat.completions.create(
      model=chat_model,
      messages=prompt,
      extra_body=rag_params
    )

    response_content = response.choices[0].message.content
    print(response_content)
    
    # Add the response to the prompt for context in the next iteration
    prompt.append({"role": "assistant", "content": response_content})


if __name__ == "__main__":
  main()
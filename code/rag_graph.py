from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_aws import ChatBedrock
import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from langchain_community.chat_models import BedrockChat

from callback_handler import ChatOpsStreamingHandler


load_dotenv()


# Initialise chat model
def get_chat_model():
    try:
        params = {
            "service_name": "bedrock-runtime",
            "region_name": "us-east-1"
        }
        bedrock_client = boto3.client(**params)
        params = {
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "client": bedrock_client,
            "model_kwargs": {
                "temperature": 0.1
            },
            "streaming": True,
            "callbacks": [ChatOpsStreamingHandler()],
        }
        bedrock_llm = BedrockChat(**params)
        return bedrock_llm

    except Exception as e:
        print(e)
        print("Error in get_bedrock_llm_model")
        raise e

# Initialise Cypher generation model
def get_cypher_llm_model():
    try:
        cypher_llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"temperature": 0.1},
        )
        return cypher_llm

    except Exception as e:
        print(e)
        print("Error in getting cypher_llm")
        raise e

# Initialise graph
def connect_to_graph():
    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4j_DB_URL"),
            username="neo4j",
            password=os.getenv("NEO4J_PASSWORD")
        )
        return graph
    except Exception as e:
        print(e)
        print("Error in connecting to graph")
        raise e

# Generate response for a prompt
def generate_response(input_text):
    cypher_llm = get_cypher_llm_model()
    chat_model = get_chat_model()
    graph = connect_to_graph()

    chain = GraphCypherQAChain.from_llm(
        cypher_llm=cypher_llm,
        qa_llm=chat_model,
        graph=graph,
        verbose=True
    )
    chain.invoke({"query": input_text})
    for token in chat_model.callbacks[0].tokens:
        yield token

# Run streamlit app
def run_streamlit_app():
    st.title('🦜🔗 Quickstart App')
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(generate_response(prompt))
        st.session_state.messages.append(
            {"role": "assistant", "content": response})

# Run app
run_streamlit_app()

import sys
import toml
from omegaconf import OmegaConf
from vRAGquery import RAGQueryVect
import os
import time
import json

from PIL import Image
import streamlit as st
from streamlit_pills import pills

from dotenv import load_dotenv
#from llama_index import SimpleDirectoryReader
#from llama_index.indices import VectaraIndex
#from langchain.embeddings import OpenAIEmbeddings, CohereEmbeddings
#from langchain.chat_models.openai import ChatOpenAI


# Load environment variables from .env file
#load_dotenv()
load_dotenv(".streamlit/secrets.toml")

# Access secrets from the secret file (or env variables)
corpus_ids = st.secrets.get("corpus_ids")
customer_id = st.secrets.get("customer_id")
api_key = st.secrets.get("api_key")
description = st.secrets.get("description")



with open("config.json") as f:
    config = json.load(f)

#source_data_desc = config["source_data_desc"]
#description = config["description"]
#title = config["title"]    



#As the second argument, the default value to use if the key is not found in config.json
source_data_desc = config.get("source_data_desc", os.environ.get("source_data_desc", "."))
description = config.get("description", os.environ.get("description", "."))
title = config.get("title", os.environ.get("title", ".")) 
title2 = config.get("title2", os.environ.get("title2", ".")) 

# Assuming your logos are named logo1.png, logo2.png, etc.
logos = ['logo1.png', 'logo2.png', 'logo3.png']  # Adjust file names as needed


def PaulVectaraRAGChat():
    def generate_response(question):
        response = vq.promptquery(question)
        return response

    if 'cnfg' not in st.session_state:
        corpus_ids = str(os.environ['corpus_ids']).split(',')
        cnfg = OmegaConf.create({
            'customer_id': str(os.environ['customer_id']),
            'corpus_ids': corpus_ids,
            'api_key': str(os.environ['api_key']),
            'title': title, #os.environ['title'],
            'title2': title2,
            'description': description, #os.environ['description'],
            'source_data_desc': source_data_desc, #os.environ['source_data_desc'],
            'prompt_name': os.environ.get('prompt_name', None)
        })
        st.session_state.cnfg = cnfg
        st.session_state.vq = RAGQueryVect(cnfg.api_key, cnfg.customer_id, cnfg.corpus_ids, cnfg.prompt_name)

    cnfg = st.session_state.cnfg
    vq = st.session_state.vq
    st.set_page_config(page_title=cnfg.title, layout="centered")
    


    
    # left side content
    with st.sidebar:
        col1, _ = st.sidebar.columns(2)  # Create two columns (use one for logos)
        for logo in logos:
            with col1:
                image = Image.open(logo)
                st.image(image,width=250)

        st.markdown(f"## RAG based app: {cnfg.title}\n\n"
                    f"This app uses AI Retrieval Augmented Generation to index and query from an uploaded corpus at Vectara database \n")

        st.markdown("---")
        st.markdown(
            "## Swift Snapshot\n"
            "During an International Hackathon by Lablab.AI, the mission was to develop advanced RAG apps and chatbots,\n "
            "integrating cutting-edge technologies such as Vectara, LlamaIndex, Together AI, and Unstructured.io.\n\n"
            
            "Built this GenAI app using the ***Query and Summarization APIs*** and leveraging the Chat API to efficiently \n"
            "retrieve information from the Vectara corpus, providing accurate breif responses to your inquiries. \n\n"
            "I seamlessly imported data into a Vectara corpus, utilizing its's ***Indexing API***.\n"
        )
        st.markdown("---")
        st.markdown(
            "\n\n"
            "Vectara’s newest embedding model BOOMERANG has been used which encodes text from the data as “vector embeddings” \n "
            "and is used to power the high performance retrieval process that is part of the RAG pipeline.\n\n "
            "UNSTRUCTURED is a Python library that brings advanced preprocessing of various file types, and simplifies the ingest of data in RAG pipelines."
        )
        st.markdown("---")
        st.markdown("©️replypaul@gmail")
        #st.image(image, width=550)

    st.markdown(f"<center> <h3> ::  {cnfg.title}  :: \n\n <h4> {cnfg.title2} </h4> </h3> </center>", unsafe_allow_html=True)
    st.markdown(f"<center> {cnfg.description}  </center>", unsafe_allow_html=True)

    selectedExample = pills("",
            [   
                "Confused about Systems Innovation, Systems Thinking, Systems Theory, Systemic Design,  and Design Thinking?",
                "Teach me Systemic Design of Socio-technical Systems?", "Systemic Design Toolkit's methodology activity",
                "What are Systems Design Principles?", "How Systemic Design related to design thinking?",
                "What are the Key Dimensions to Systems Innovation?", "What is Systems Mapping?",
                "What we can know from Mexico City Water System?", "Teach me Systems Thoery",
                "What are the Systemic Design Principles for Complex Social Systems?",
                
            ], ["✨","✨","✨","✨","✨","✨","✨","✨","✨","✨"],
            clearable=False,
            index=0,
        )
    #st.write( selectedExample+ "  <---  *Copy, paste/ or modify it at the bottom input bar*" )
    st.markdown("*Some examples above to click.  OR Type your Qs inside the input bar at bottom*")

    placeholder_value = f"✍️ Type '{selectedExample}' here ✍️"

    

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Hi!  Ask me to help you briefly on above topics around complex systems!"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    # Accept user input from the provided prompt
    if prompt := st.chat_input(placeholder=placeholder_value, max_chars=250) or selectedExample:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.write("**You:**")
            st.markdown(prompt)

    
    # Display a new assistant response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Indexing > Summarizing..."):
                response = generate_response(prompt) 
                st.write("**SystemiX Bot:** ")
                st.write(response) 
 
        st.session_state.messages.append({"role": "assistant", "content": response})
if __name__ == "__main__":
    PaulVectaraRAGChat()
    
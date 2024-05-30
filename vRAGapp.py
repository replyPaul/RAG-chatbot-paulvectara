import sys
import toml
from omegaconf import OmegaConf
from vRAGquery import RAGQueryVect
import os
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


#As the second argument, the default value to use if the key is not found in config.json
source_data_desc = config.get("source_data_desc", os.environ.get("source_data_desc", "."))
description = config.get("description", os.environ.get("description", "."))
title = config.get("title", os.environ.get("title", ".")) 
title2 = config.get("title2", os.environ.get("title2", ".")) 
title3 = config.get("title3", os.environ.get("title3", ".")) 


st.set_page_config(page_title=title,  page_icon="🎡", layout="centered")
st.markdown(
    """
    <style>
        @import 'https://fonts.googleapis.com/css2?family=Orbitron&display=swap';
        .pixel-font {
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
        """<div class="pixel-font"><center> ::  SYSTEMiX BOT  :: </center></div>
    """,
        unsafe_allow_html=True,
    )


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
            'title3': title3,
            'description': description, #os.environ['description'],
            'source_data_desc': source_data_desc, #os.environ['source_data_desc'],
            'prompt_name': os.environ.get('prompt_name', None)
        })
        st.session_state.cnfg = cnfg
        st.session_state.vq = RAGQueryVect(cnfg.api_key, cnfg.customer_id, cnfg.corpus_ids, cnfg.prompt_name)

    cnfg = st.session_state.cnfg
    vq = st.session_state.vq
    #st.set_page_config(page_title=cnfg.title, layout="centered")
    
    st.markdown(f"<center><h4> {cnfg.title2} </h4></center>", unsafe_allow_html=True)
    st.markdown(f"<center> {cnfg.description}  </center>", unsafe_allow_html=True)


    # left side content
    with st.sidebar:
        image1 = Image.open('logo3.png')
        st.image(image1,width=280)
        st.markdown(f"## {cnfg.title}\n\n"
                    f"A ***hybrid search*** application for generative summarization, utilizing both semantic and keyword-based search, supported by Grounded Generation (GG) powered by Vectara and its ecosystem tools. \n\n"
                    f"---\n"
                    f"Created the GenAI app by integrating the ***Query and Summarization APIs***, and the Chat API to efficiently extract summarized responses from a small database of PDF, PPT, DOCX, HTML, TXT files ingested at vectara corpus using ***Ingesting API***. \n"
                    )#f"Built this GenAI app using the ***Query and Summarization APIs*** and leveraging the Chat API to efficiently retrieve information from an uploaded corpus of PDF,PPT,DOCX,MD,WEB files of database. \n")
        
        st.markdown("---")
        st.markdown(f" {cnfg.title3}\n")
        #st.write("Created in an International AI hackathon  NNGroup - APRIL 2024 - Paul Biswa \n")
        st.markdown("---")
        #col1, _ = st.sidebar.columns(2)  # Create two columns (use one for logos)
       
        #st.markdown(
        #   "\n\n"
        #     "UNSTRUCTURED is a Python library that brings advanced preprocessing of various file types, and simplifies the ingest of data in RAG pipelines.\n"
        #)
        st.markdown("Stages within RAG")
        image2 = Image.open('Calibrate.png')
        st.image(image2,width=280)
        st.markdown("---")
        image = Image.open('logo1.png')
        st.image(image,width=280)

    selectedExample = pills("",
            [   
                "Confused about Systems Thinking, Systems Theory, Systemic Design, Systems Innovation, and Design Thinking?",
                #"What do u think about complex wicked system?", "Systemic Design Toolkit's methodology activity",
                "What are Systems Design Principles?","What is exactly SYSTEMIC DESIGN?","What is Systems Mapping?", 
                "Why Systems Innovation For Circular Economy?", "Combo of Systems Thinking + Design Thinking == ?",
                "Key Dimensions to Systems Thinking?",  "What we can know from Bangalore City Water System?", 
                "What are the Systemic Design Principles for Complex Social Systems?", "Tell me about Systems Thoery",
            ], ["✨","✨","✨","✨","✨","✨","✨","✨","✨","✨"],  
            clearable=False,
            index=0,
       )
    placeholder_value = f"✍️ Ask Questions "
    #st.write( selectedExample+ "  <---  *Copy, paste/ or modify it at the bottom input bar*" )
    #st.text("PS: due to cloud python verison mismatch, sometimes examples are not rendering")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Few examples above to click.  Or Ask me your Queries around complex systems thinking!"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    # Accept user input from the provided prompt
    if prompt := st.chat_input(placeholder=placeholder_value, max_chars=350) or selectedExample:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.write("**You:**")
            st.markdown(prompt)

    
    # Display a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Indexing  >>  Summarizing..."):
                response = generate_response(prompt) 
                st.write("**SystemiX Bot:** ")
                st.write(response) 
 
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    PaulVectaraRAGChat()
    
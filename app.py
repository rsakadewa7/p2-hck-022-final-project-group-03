import openai
import PyPDF2
import streamlit as st
from pymongo import MongoClient
from langchain.chat_models import ChatOpenAI  # Use ChatOpenAI for GPT-4
from langchain.chains import ConversationChain

# Set up OpenAI API key
api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

# MongoDB Connection
MONGO_URI = "mongodb+srv://mongo:mongo@servermongo.wltff.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["finpro"]
jobs_collection = db["jobs"]

# LangChain setup
llm = ChatOpenAI(openai_api_key=api_key, temperature=0.7)  # Use OpenAI GPT model
conversation = ConversationChain(llm=llm)

# Function to extract text from PDF (if needed for other purposes)
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to query job database with case-insensitive matching
def query_jobs(skills):
    # Convert skills to lowercase for consistent matching
    skills = [skill.lower() for skill in skills]
    query = {"skills": {"$in": skills}}
    matching_jobs = list(jobs_collection.find(query))
    return matching_jobs

# Function to extract skills from a sentence using LLM
def extract_skills_from_sentence(sentence):
    prompt = f"Extract the skills from the following sentence: '{sentence}'"
    response = llm(prompt)
    skills = response.strip().split(", ")
    return [skill.lower() for skill in skills]

# Streamlit UI
st.title("Job Search Assistant")

sentence_input = st.text_input("Enter a sentence describing your skills:")

if sentence_input:
    with st.spinner("Extracting skills from your sentence..."):
        skills = extract_skills_from_sentence(sentence_input)
    
    st.write("**Identified Skills:**")
    st.write(skills)
    
    # Query job database for matching jobs
    with st.spinner("Searching for jobs matching your skills..."):
        matching_jobs = query_jobs(skills)
    
    if matching_jobs:
        st.success(f"Found {len(matching_jobs)} job openings matching your skills!")
        
        # Display the job results in a table
        st.write("**Job Links:**")
        for job in matching_jobs:
            st.markdown(f"- **{job['job_title']} at {job['company_name']}**: [{job['job_link']}]({job['job_link']})")
    else:
        st.warning("No matching job openings found at this time. Please try again later.")

        
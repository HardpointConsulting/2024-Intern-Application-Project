import streamlit as st
import psycopg2
from PyPDF2 import PdfReader
from datetime import datetime
import os
import pytesseract
from PIL import Image
import google.generativeai as genai

genai.configure(api_key='AIzaSyD6HL9315oCQIYgYdvA1z8xU4z5ysuuPbw')
generation_config={"temperature": 0.9,"top_p": 1,"top_k": 1,"max_output_tokens": 2048}
# Set path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]
model = genai.GenerativeModel('gemini-1.0-pro-latest')
convo = model.start_chat(history=[])

# Database connection
conn = psycopg2.connect(
    dbname="internship",
    user="postgres",
    password="soloman",
    host="localhost"
)
cur = conn.cursor()

# Function to extract text from an image using Tesseract OCR
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)


# Function to extract metadata and text from PDF and insert it into the database
def extract_metadata_and_insert(pdf_file):
    pdf = PdfReader(pdf_file)
    metadata = pdf.metadata

    for page_number in range(len(pdf.pages)):
        image = pdf.pages[page_number].to_image()
        text = extract_text_from_image(image)

        # Send prompts to Gemini for specific information extraction
        try:
            convo.send_message(
                f'''
                    Get the title of the text provided in {text}.
                    Return the output as a string of the exact name as the title of the content.
                    Do not add any other content of your own in the output.
                '''
            )
            title=convo.last.text
            convo.send_message(
                f'''
                    Get the year of the text provided in {text}.
                    Return the output as a string of the exact year as the year of the content.
                    Do not add any other content of your own in the output.
                '''
            )
            year=int(convo.last.text)
            convo.send_message(
                f'''
                    Get the journal of publication of the text provided in {text}.
                    Return the output as a string of the exact journal as the journal of the content.
                    Do not add any other content of your own in the output.
                '''
            )
            journal=convo.last.text
            convo.send_message(
                f'''
                    Get the names of the authors in {text}.
                    Return the output as a string of all the names of authors separated by commas.
                    Do not add any other content of your own in the output.
                '''
            )
            authors=convo.last.text
            convo.send_message(
                f'''
                    Get the type of the text provided in {text}.
                    Return the output as a string of the type of the content.
                '''
            )
            genre=convo.last.text
            convo.send_message(
                f'''
                    Get the short description of the text provided in {text}.
                    Return the output as a string of the description of the content.
                '''
            )
            description=convo.last.text
            convo.send_message(
                f'''
                    Get the focal constructs of the text provided in {text}.
                    Return the output as a string of the focal constructs of the content.
                '''
            )
            constructs=convo.last.text
            convo.send_message(
                f'''
                    Get the theoretical perspectives of the text provided in {text}.
                    Return the output as a string of the theoretical perspectives of the content.
                '''
            )
            perspectives=convo.last.text
            convo.send_message(
                f'''
                    Get the context of the text provided in {text}.
                    Return the output as a string of the context of the content.
                '''
            )
            context=convo.last.text
            convo.send_message(
                f'''
                    Get the study design of the text provided in {text}.
                    Return the output as a string of the study design of the content.
                '''
            )
            study=convo.last.text
            convo.send_message(
                f'''
                    Get the levels of the text provided in {text}.
                    Return the output as a string of the levels of the content.
                '''
            )
            levels=convo.last.text
            convo.send_message(
                f'''
                    Get the findings of the text provided in {text}.
                    Return the output as a string of the findings of the content.
                '''
            )
            findings=convo.last.text
            convo.send_message(
                f'''
                    Get the summary of the text provided in {text}.
                    Return the output as a string of the summary of the content.
                '''
            )
            summary=convo.last.text
        except Exception as e:
                i=i-1
                continue 

        # Use extracted creation date from metadata or parse creation_date_str to datetime object
        creation_date = metadata.get('/CreationDate', '')

        cur.execute("INSERT INTO pdf (author, title, creation_date, description, year, journal, genre) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (authors, title, creation_date, description, year, journal, genre))
        conn.commit()

# Streamlit app
st.title("PDF Upload and View")
# Authenticate with Gemini API

# File upload
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file is not None:
    st.write("File Uploaded Successfully")
    extract_metadata_and_insert(uploaded_file)

# View table contents
st.subheader("Table Contents")
cur.execute("SELECT * FROM pdf")
rows = cur.fetchall()
for row in rows:
    st.write(row)

# Close database connection
cur.close()
conn.close()

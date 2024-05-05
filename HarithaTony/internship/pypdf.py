from PyPDF2 import PdfReader
from transformers import pipeline
import dotenv
import torch

  
dotenv.load_dotenv()

reader = PdfReader("assitant for visually impaired.pdf")
text = ""
meta = reader.metadata
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text()
def pdf_title():
    return meta.title #title
def pdf_date():
    return meta.creation_date #date
def pdf_journal():
    return meta.subject
def pdf_author():
    try:
        with open("sample.txt", "w", encoding='utf-8') as file:
            file.write(text)
            print("File created successfully.")
    except Exception as e:
            print("An error occurred:", str(e)) 

    ner = pipeline("ner", grouped_entities=True)
    t = ner(text)
    auth = []
    for i in range(len(t)):
        if t[i]['entity_group'] == 'PER':
            if(len(t[i]['word'])<=1):
                auth.append(t[i]['word'].replace(",","").replace("\'","").replace(" ","").replace("  ","") + ".")  #removing unwanted characters and white-spaces
            else:
                auth.append(t[i]['word'] + ",")
    auth_name = " ".join(auth)
    return auth
# Initialize the summarization pipeline
def pdf_summary():
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Load text from a file
    file_path = "sample.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Split the text into smaller chunks
    max_chunk_length = 512  # Maximum sequence length supported by the model
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]

    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, min_length=10, max_length=30)[0]['summary_text']
        summaries.append(summary)

    # Combine the summaries into a single summary
    final_summary = ' '.join(summaries)
    return final_summary
import pypdf
import spacy
nlp = spacy.load("en_core_web_sm")

def extract_names_from_pdf(pdf_path):
    names = []
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = pypdf.PdfReader(pdf_file)
        page = pdf_reader.pages[0]
        text = page.extract_text()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append(ent.text)
    return names

# Example usage
def authors():
    pdf_path = "paper1.pdf"
    names_list = extract_names_from_pdf(pdf_path)
    return(names_list)



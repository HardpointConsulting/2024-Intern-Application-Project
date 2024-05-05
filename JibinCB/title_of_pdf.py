import pypdf
import re

# Open the PDF file
def title():
    pdf_file = open('paper1.pdf', 'rb')

    # Initialize PDF reader
    pdf_reader = pypdf.PdfReader(pdf_file)

    # Extract text from the first page
    first_page = pdf_reader.get_page(0)
    pdf_text_first_page = first_page.extract_text(0)
    pdf_file.close()

    fully_capitalized_text = re.findall(r'\b[A-Z\s\.\-]+\b', pdf_text_first_page)

    title = fully_capitalized_text[0].strip()
    return(title)

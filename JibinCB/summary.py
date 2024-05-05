import pypdf
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = pypdf.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text


def summarize_text(text, sentences_count=20):
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sentences = summarizer(parser.document, sentences_count)
    summary = " ".join(str(sentence) for sentence in sentences)
    return summary


# Example usage
def summary_of_pdf():
    pdf_path = "paper1.pdf"
    pdf_text = extract_text_from_pdf(pdf_path)
    summary_text = summarize_text(pdf_text)
    return(summary_text)

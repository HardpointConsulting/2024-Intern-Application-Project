from django.shortcuts import render
from django.conf import settings
import os
import convertapi
import pytesseract as pyt
from PIL import Image
import google.generativeai as genai
import PyPDF2
from openpyxl import Workbook
from .models import *
from dotenv import load_dotenv

load_dotenv()

def home(request):
    #Home page of the website
    return render(request,'upload.html')

def upload(request):
    #Handling file upload
    if request.method=='POST' and request.FILES.get('pdf'):
        pdf_file=request.FILES['pdf']
        file_path=os.path.join(settings.MEDIA_ROOT,'pdfs',pdf_file.name)
        
        # Save the uploaded file
        with open(file_path,'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        #Finding out the number of pages in the uploaded pdf
        with open(file_path,'rb') as file:
            pdf_reader=PyPDF2.PdfReader(file)
            pages=len(pdf_reader.pages)

        #Data pre-processing
            #1. Split pdf into individual pages
            #2. Convert .pdf to .png format using api
        # Code snippet is using the ConvertAPI Python Client: https://github.com/ConvertAPI/convertapi-python
        convertapi.api_secret=os.getenv('API_SECRET')
        convertapi.convert('png',{'File': file_path},from_format='pdf').save_files('media/pngs')

        #Configure tesseract ocr
        pyt.pytesseract.tesseract_cmd="C:\\Users\\Vishnu\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"

        #Extract the name of the pdf without the extension
        dot_index=pdf_file.name.rfind('.')
        if dot_index!=-1:
            name=pdf_file.name[:dot_index]
        else:
            name=pdf_file.name
        
        #Configure Google Gemini api for prompting
        genai.configure(api_key=os.getenv('API_KEY'))
        generation_config={"temperature": 0.9,"top_p": 1,"top_k": 1,"max_output_tokens": 2048}
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
        model = genai.GenerativeModel(model_name="gemini-1.0-pro", generation_config=generation_config,safety_settings=safety_settings)
        convo = model.start_chat(history=[])

        os.remove(file_path) #Delete pdf file from the folder after pre-processing
        
        #Clear all previous entries in the database table
        if Output.objects.exists():
            Output.objects.all().delete()

        #passing pages one by one to the llm for prompting
        for i in range(1,pages+1):
            if i==1:
                file_path=f'media/pngs/{name}.png'
                content=pyt.image_to_string(Image.open(file_path))
            else:
                file_path=f'media/pngs/{name}-{i}.png'
                content=pyt.image_to_string(Image.open(file_path))
            try:
                convo.send_message(
                    f'''
                        Get the title of the text provided in {content}.
                        Return the output as a string of the exact name as the title of the content.
                        Do not add any other content of your own in the output.
                    '''
                )
                title=convo.last.text
                convo.send_message(
                    f'''
                        Get the year of the text provided in {content}.
                        Return the output as a string of the exact year as the year of the content.
                        Do not add any other content of your own in the output.
                    '''
                )
                year=int(convo.last.text)
                convo.send_message(
                    f'''
                        Get the journal of publication of the text provided in {content}.
                        Return the output as a string of the exact journal as the journal of the content.
                        Do not add any other content of your own in the output.
                    '''
                )
                journal=convo.last.text
                convo.send_message(
                    f'''
                        Get the names of the authors in {content}.
                        Return the output as a string of all the names of authors separated by commas.
                        Do not add any other content of your own in the output.
                    '''
                )
                authors=convo.last.text
                convo.send_message(
                    f'''
                        Get the type of the text provided in {content}.
                        Return the output as a string of the type of the content.
                    '''
                )
                genre=convo.last.text
                convo.send_message(
                    f'''
                        Get the short description of the text provided in {content}.
                        Return the output as a string of the description of the content.
                    '''
                )
                description=convo.last.text
                convo.send_message(
                    f'''
                        Get the focal constructs of the text provided in {content}.
                        Return the output as a string of the focal constructs of the content.
                    '''
                )
                constructs=convo.last.text
                convo.send_message(
                    f'''
                        Get the theoretical perspectives of the text provided in {content}.
                        Return the output as a string of the theoretical perspectives of the content.
                    '''
                )
                perspectives=convo.last.text
                convo.send_message(
                    f'''
                        Get the context of the text provided in {content}.
                        Return the output as a string of the context of the content.
                    '''
                )
                context=convo.last.text
                convo.send_message(
                    f'''
                        Get the study design of the text provided in {content}.
                        Return the output as a string of the study design of the content.
                    '''
                )
                study=convo.last.text
                convo.send_message(
                    f'''
                        Get the levels of the text provided in {content}.
                        Return the output as a string of the levels of the content.
                    '''
                )
                level=convo.last.text
                convo.send_message(
                    f'''
                        Get the findings of the text provided in {content}.
                        Return the output as a string of the findings of the content.
                    '''
                )
                findings=convo.last.text
                convo.send_message(
                    f'''
                        Get the summary of the text provided in {content}.
                        Return the output as a string of the summary of the content.
                    '''
                )
                summary=convo.last.text
            except Exception as e:
                i=i-1
                continue

            #Stores the title,authorand alternate title in the database
            output=Output(id=i,title=title,year=year,journal=journal,authors=authors,description=description,constructs=constructs,context=context,study=study,level=level,findings=findings,summary=summary)
            output.save()
            os.remove(file_path)

        response=Output.objects.all()
        return render(request,'view.html',{'response':response})
    else:
        error = "Upload PDF"
        return render(request,'error.html',{'error':error})

def create(request):
    data=Output.objects.all()
    
    wb=Workbook()
    ws=wb.active

    ws.append(['S No.','Title','Year','Journal','Authors','Description','Constructs','Context','Study','Level','Findings','Summary'])
    for i in data:
        ws.append([i.id,i.title,i.year,i.journal,i.authors,i.description,i.constructs,i.context,i.study,i.level,i.findings,i.summary])

    file_path = os.path.join(settings.MEDIA_ROOT,'excel','titlr.xlsx')

    wb.save(file_path)
    return render(request,'download.html')
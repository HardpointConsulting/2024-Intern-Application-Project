from django.shortcuts import render,redirect
from django.conf import settings
import os
import convertapi
import pytesseract as pyt
from PIL import Image
import google.generativeai as genai
import PyPDF2
from .models import *
from dotenv import load_dotenv
from openpyxl import Workbook

load_dotenv()

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

def home(request):
    #Home page of the website
    return render(request,'upload.html')

def saved(request):
    response=Save.objects.all()

    return render(request,'saved.html',{'response':response})

def upload(request):
    #Remove any existing pdfs and pngs
    pdfs = os.listdir('media/pdfs')
    pngs = os.listdir('media/pngs')
    for pdf,png in zip(pdfs,pngs):
        pdf_path = os.path.join('media/pdfs', pdf)
        png_path = os.path.join('media/pngs', png)
        os.remove(pdf_path)
        os.remove(png_path)

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
        pyt.pytesseract.tesseract_cmd='Tesseract-OCR/tesseract.exe'

        #Extract the name of the pdf without the extension
        dot_index=pdf_file.name.rfind('.')
        if dot_index!=-1:
            name=pdf_file.name[:dot_index]
        else:
            name=pdf_file.name

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
                levels=convo.last.text
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

            #Stores the data in the database
            output=Output(
                id=i,
                title=title,
                year=year,
                journal=journal,
                authors=authors,
                genre=genre,
                description=description,
                constructs=constructs,
                perspectives=perspectives,
                context=context,
                study=study,
                levels=levels,
                findings=findings,
                summary=summary
            )
            output.save()
            os.remove(file_path) #Remove page from folder once information is extracted
        
        #passing object of table to frontend
        response=Output.objects.all()
        return render(request,'view.html',{'response':response})
    else:
        error = "Upload PDF"
        return render(request,'error.html',{'error':error})

def edit(request):
    if request.method == 'POST':
        ids=request.POST.getlist('id')
        titles=request.POST.getlist('title')
        years=request.POST.getlist('year')
        journals=request.POST.getlist('journal')
        authors=request.POST.getlist('authors')
        genres=request.POST.getlist('genre')
        descriptions=request.POST.getlist('description')
        constructs=request.POST.getlist('constructs')
        perspectives=request.POST.getlist('perspectives')
        contexts=request.POST.getlist('context')
        studies=request.POST.getlist('study')
        levels=request.POST.getlist('levels')
        notes=request.POST.getlist('notes')
        findings=request.POST.getlist('findings')
        summaries=request.POST.getlist('summary')
        
        Output.objects.all().delete()
        
        for id,title,year,journal,author,genre,description,construct,perspective,context,study,level,note,finding,summary in zip(
            ids,titles,years,journals,authors,genres,descriptions,constructs,perspectives,contexts,studies,levels,notes,findings,summaries
        ):
            output=Output(
                id=id,
                title=title,
                year=year,
                journal=journal,
                authors=author,
                genre=genre,
                description=description,
                constructs=construct,
                perspectives=perspective,
                context=context,
                study=study,
                levels=level,
                notes=note,
                findings=finding,
                summary=summary
            )
            output.save()
        
        return render(request,'research.html')
    
    else:
        error = "Unauthorized access"
        return render(request,'error.html',{'error':error})
    
def research(request):
    if request.method == 'POST':
        research=request.POST.get('research')
        contents=Output.objects.all()
        i=1
        for content in contents:
            try:
                convo.send_message(
                    f'''
                        Get the insights related to {research} question based on the data provided in {content}.
                        Return the output as a string of the insights.
                    '''
                )
                insights=convo.last.text
                convo.send_message(
                    f'''
                        Get any quotable points related to {research} based on the data provided in {content}.
                        Return the output as a string of quotable points.
                    '''
                )
                points=convo.last.text
                convo.send_message(
                    f'''
                        Get the potential use of {research} question based on the data provided in {content}.
                        Return the output as a string of the potential use.
                    '''
                )
                use=convo.last.text
            except Exception as e:
                research(request)
            
            output=Output.objects.get(id=i)
            output.insights=insights
            output.points=points
            output.use=use
            output.save()
            i+=1

        response=Output.objects.all()
        return render(request,'review.html',{'response':response})
    
    else:
        error = "Unauthorized access"
        return render(request,'error.html',{'error':error})
    
def save(request):
    if request.method == 'POST':
        additionals=request.POST.getlist('additional')
        i=1
        for additional in additionals:
            output=Output.objects.get(id=i)
            output.additional=additional
            output.save()
            i+=1

        values=Output.objects.all()
        for value in values:
            save=Save(
                title=value.title,
                year=value.year,
                journal=value.journal,
                authors=value.authors,
                genre=value.genre,
                description=value.description,
                constructs=value.constructs,
                perspectives=value.perspectives,
                context=value.context,
                study=value.study,
                levels=value.levels,
                notes=value.notes,
                findings=value.findings,
                summary=value.summary,
                insights=value.insights,
                points=value.points,
                use=value.use,
                additional=value.additional
            )
            save.save()
        
        return render(request,'save.html')
    
    else:
        error = "Unauthorized access"
        return render(request,'error.html',{'error':error})
    
def trash(request):
    Save.objects.all().delete()

    return redirect('home')

def create(request):
    data=Save.objects.all()
    
    wb=Workbook()
    ws=wb.active

    ws.append([
        'S No.',
        'Title',
        'Year',
        'Journal',
        'Authors',
        'Genre',
        'Description',
        'Constructs',
        'Perspectives',
        'Context',
        'Study',
        'Levels',
        'Notes',
        'Findings',
        'Summary',
        'Insights',
        'Points',
        'Use',
        'Additional'
    ])
    for i in data:
        ws.append([
            i.id,
            i.title,
            i.year,
            i.journal,
            i.authors,
            i.genre,
            i.description,
            i.constructs,
            i.perspectives,
            i.context,
            i.study,
            i.levels,
            i.notes,
            i.findings,
            i.summary,
            i.insights,
            i.points,
            i.use,
            i.additional
        ])

    file_path = os.path.join(settings.MEDIA_ROOT,'excel','xtrkt.xlsx')

    wb.save(file_path)
    return render(request,'download.html')
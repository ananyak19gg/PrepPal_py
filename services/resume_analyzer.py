import pdfplumber
import easyocr
from PIL import Image 
from openai import OpenAI
import os
import json

reader = easyocr.Reader(['en'])
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from pdf bro"""
    text = ' '
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text +=page.extract_text() or ""
    return text

def extract_text_from_image(file_path: str) -> str:
    result = reader.readtext(file_path, detail=0, paragraph=True)
    text = " ".join(result)
    return text

def structure_resume_data(resume_text: str) -> dict:
    #structure resume text into JSON format
    return {
        "extractedText": resume_text,
        "wordCount": len(resume_text.split()),
        "characterCount": len(resume_text)
    }

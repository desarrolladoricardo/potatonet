
import os
from pypdf import PdfReader
from docx import Document

def extract_pdf(path):
    print(f"--- Extracting PDF: {path} ---")
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print(text[:2000]) # Print first 2000 chars to avoid huge output
        if len(text) > 2000:
            print("...[truncated]...")
    except Exception as e:
        print(f"Error reading PDF: {e}")

def extract_docx(path):
    print(f"--- Extracting DOCX: {path} ---")
    try:
        doc = Document(path)
        text = "\n".join([p.text for p in doc.paragraphs])
        print(text)
    except Exception as e:
        print(f"Error reading DOCX: {e}")

if __name__ == "__main__":
    pdf_path = "/home/r/Descargas/ACA_INVESTIGACION DE OPERACIONES.pdf"
    docx_path = "/home/r/Escritorio/redes papa/Fortalecimiento del Cultivo de Papa en Boyacá a través de una Red de Articulación Productiva  (POTATONET).docx"
    
    if os.path.exists(pdf_path):
        extract_pdf(pdf_path)
    else:
        print(f"PDF not found at {pdf_path}")
        
    if os.path.exists(docx_path):
        extract_docx(docx_path)
    else:
        print(f"DOCX not found at {docx_path}")

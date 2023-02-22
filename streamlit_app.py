import streamlit as st
import pytesseract
import PyPDF2
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


st.write("Hello World")

uploaded_file = st.file_uploader("Choose a file")

# image = Image.open(uploaded_file)

# text = pytesseract.image_to_string(image)
# st.write(text)


pdf_reader = PyPDF2.PdfReader(uploaded_file)
text = ''
for page_num in range(len(pdf_reader.pages) ):
    page = pdf_reader.pages[page_num]
    text += page.extract_text()
recognized_text = pytesseract.image_to_string(text)
st.write(recognized_text)
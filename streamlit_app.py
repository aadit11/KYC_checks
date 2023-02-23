import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Users\SAHIL\Downloads\Release-23.01.0-0\poppler-23.01.0\Library\bin"

st.subheader("Please upload a PDF or image file for text recognition!")

accepted_file_extensions = ['pdf', 'png', 'jpg', 'jpeg']

uploaded_file = st.file_uploader(
    "Choose a file", type=accepted_file_extensions)


def process_image(image):
    text = pytesseract.image_to_string(image)
    st.write(text)


if uploaded_file:

    file_extension = uploaded_file.name.split('.')[-1]
    image_extensions = accepted_file_extensions[1:]

    if file_extension in image_extensions:

        image = Image.open(uploaded_file)
        process_image(image)

    else:

        with io.BytesIO(uploaded_file.read()) as pdf_file:
            images = convert_from_bytes(pdf_file.read(
            ), poppler_path=poppler_path)

        for i, img in enumerate(images):
            # st.image(img, caption=f'PDF page {i+1}')
            process_image(img)

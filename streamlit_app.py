import streamlit as st
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    'pytesseract.pytesseract.tesseract_cmd')
poppler_path = os.getenv('poppler_path')

st.subheader("Please upload a PDF or image file for text recognition!")

accepted_file_extensions = ['pdf', 'png', 'jpg', 'jpeg']

uploaded_file = st.file_uploader(
    "Choose a file", type=accepted_file_extensions)


def process_image(image):
    # Set the configuration options for pytesseract
    config = '--psm 6'

    # Get the recognized text with line breaks
    text = pytesseract.image_to_string(image, config=config)

    # Split the text into lines and store them in a list
    lines = text.split('\n')

    # Print the lines
    for line in lines:
        st.write(line)


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

# SBI
# bank name
# account name
# account no
# address
# branch
# nomination registered - y/n
# balance

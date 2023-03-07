import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from fpdf import FPDF
import io
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# pytesseract.pytesseract.tesseract_cmd = os.getenv('pytesseract.pytesseract.tesseract_cmd')
# poppler_path = os.getenv('poppler_path')
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
# poppler_path = os.getenv('poppler_path')

st.subheader("Please upload a PDF or image file for text recognition!")

accepted_file_extensions = ['pdf', 'png', 'jpg', 'jpeg']

uploaded_file = st.file_uploader(
    "Choose a file", type=accepted_file_extensions)


def generate_pdf(bank_line, account_name_line, account_no_line, address_line, branch_line, nomination_required_line, balance_line):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    pdf.multi_cell(0, 10, bank_line + "\n" + account_name_line + "\n" + account_no_line + "\n" +
                   address_line + "\n" + branch_line + "\n" + nomination_required_line + "\n" + balance_line)

    filename = "bank_statement"+datetime.now().strftime("%d-%m-%Y,%H:%M:%S")+".pdf"
    st.download_button("Download Report", data=pdf.output(
        dest='S').encode('latin-1'), file_name=filename)
    st.success('Report generated successfully!', icon="✅")


def process_image(image):
    # Set the configuration options for pytesseract
    config = '--psm 6'

    # Get the recognized text with line breaks
    text = pytesseract.image_to_string(image, config=config)

    # Split the text into lines and store them in a list
    lines = text.split('\n')

    bank_line = ''
    account_name_line = ''
    account_no_line = ''
    address_line = ''
    address_line_start_idx = 0
    address_line_end_idx = 0
    branch_line = ''
    nomination_required_line = ''
    balance_line = ''

    # Print the lines
    for i, line in enumerate(lines):
        if line.lower().count('bank') > 0:
            bank_line = line
        if line.lower().count('account name') > 0:
            account_name_line = line
        if line.lower().count('account number') > 0:
            account_no_line = line
        if line.lower().count('address') > 0:
            address_line_start_idx = i
        if line.lower().count('account type') > 0:
            address_line_end_idx = i
        if line.lower().count('branch') > 0:
            branch_line = line
        if line.lower().count('nomination') > 0:
            nomination_required_line = line
        if balance_line == '' and line.lower().count('balance as on') > 0:
            balance_line = line
        # st.write(line)

    address_line = lines[address_line_start_idx:address_line_end_idx]
    address_line = ' '.join(address_line)

    generate_pdf(bank_line, account_name_line, account_no_line,
                 address_line, branch_line, nomination_required_line, balance_line)


if uploaded_file:

    file_extension = uploaded_file.name.split('.')[-1]
    image_extensions = accepted_file_extensions[1:]

    with st.spinner('Loading'):

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

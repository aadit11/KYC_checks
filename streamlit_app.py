import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from fpdf import FPDF
import io
import os
from datetime import datetime
from dotenv import load_dotenv
import numpy as np
import cv2
import re

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    'pytesseract.pytesseract.tesseract_cmd')
poppler_path = os.getenv('poppler_path')

st.subheader("Please upload a PDF or image file for text recognition!")

accepted_file_extensions = ['pdf', 'png', 'jpg', 'jpeg']

uploaded_file = st.file_uploader(
    "Choose a file", type=accepted_file_extensions)


def generate_bank_pdf(bank_line, account_name_line, account_no_line, address_line, branch_line, nomination_required_line, balance_line):

    pdf = FPDF()
    pdf.add_page()

    # Add header image
    pdf.image('C:\IntellectProject\Images\header.jpg', x=0, y=0, w=210)

    # Add footer image
    pdf.image('C:\IntellectProject\Images\footer.jpg', x=160, y=272, w=50)

    pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(50, 78)
    pdf.multi_cell(0, 10, bank_line + "\n" + account_name_line + "\n" + account_no_line + "\n" +
                   address_line + "\n" + branch_line + "\n" + nomination_required_line + "\n" + balance_line)

    filename = "bank_statement"+datetime.now().strftime("%d-%m-%Y,%H:%M:%S")+".pdf"
    st.download_button("Download Report", data=pdf.output(
        dest='S').encode('latin-1'), file_name=filename)
    st.success('Report generated successfully!', icon="✅")


def process_image(image):
    # Load the image using OpenCV
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Preprocess the image
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, threshold = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Pass the preprocessed image to Tesseract OCR engine
    text = pytesseract.image_to_string(threshold)

    if 'balance' in text.lower():
        process_bank_statement(threshold)

    elif 'permanent account number' in text.lower():
        process_pan(threshold)

    elif 'passport number' in text.lower():
        process_passport(threshold)

    else:
        st.warning('Picture quality unclear!', icon="🚨")


def process_bank_statement(threshold):
    # Pass the preprocessed image to Tesseract OCR engine
    text = pytesseract.image_to_string(threshold, config='--psm 6')

    # Split the text into lines and store them in a list
    lines = text.split('\n')
    st.write(lines)

    # Parse the extracted text to find the name and PAN card number using regular expressions
    bank_names = ['ICICI', 'HDFC', 'SBI', 'State Bank of India',
                  'Axis', 'Kotak', 'IDBI', 'PNB', 'BOB']
    bank_pattern = re.compile(
        r'\b(' + '|'.join(bank_names) + r')\b', re.IGNORECASE)
    account_name_pattern = re.compile(
        r'Account\s*Name\s*:?\s*([A-Z][a-z]*\.?\s+[A-Z](?:\s*[a-z]*\.?\s+)?[A-Z][a-z]*)', re.IGNORECASE)
    account_number_pattern = re.compile(
        r'Account\s*Number\s*:?\s*(\d{9,20})', re.IGNORECASE)
    address_pattern = re.compile(
        r'Address\s*:?\s*([\w\s\-\.,/#&]*\d{6})', re.IGNORECASE | re.DOTALL)
    branch_pattern = re.compile(r'Branch\s*:?\s*(.*)', re.IGNORECASE)
    nomination_pattern = re.compile(
        r'(?i)\bnomination\b.*\b(yes|no)\b', re.IGNORECASE)
    balance_pattern = re.compile(
        r'\d{1,3}(?:,\d{3})*\.\d{2}', re.IGNORECASE)

    # Search for matches using the regular expressions
    bank_match = bank_pattern.search(text)
    account_name_match = account_name_pattern.search(text)
    account_number_match = account_number_pattern.search(text)
    address_match = address_pattern.search(text)
    branch_match = branch_pattern.search(text)
    nomination_match = nomination_pattern.search(text)
    balance_match = balance_pattern.findall(text)

    if bank_match:
        bank = bank_match.group(1)
    else:
        bank = "Bank name not found"

    st.write("Bank:", bank)
    st.write("Account Number:", account_number_match.group(1))
    st.write("Account Name:", account_name_match.group(1))
    st.write("Address:", address_match.group(1))
    st.write("Branch:", branch_match.group(1))
    st.write("Nomination:", nomination_match.group(1))
    st.write("Balance:", balance_match[-1])


def process_pan(threshold):
    # Apply morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate = cv2.dilate(threshold, kernel, iterations=1)
    erode = cv2.erode(dilate, kernel, iterations=1)

    # Pass the preprocessed image to Tesseract OCR engine
    text = pytesseract.image_to_string(erode)

    # Split the text into lines and store them in a list
    lines = text.split('\n')
    st.write(lines)

    # Parse the extracted text to find the name and PAN card number using regular expressions
    name_pattern = re.compile(
        r'Name\s*:?\s*(\w+\s+\w+\s+\w+)', re.IGNORECASE)
    pan_pattern = re.compile(
        r'\s*:?\s*([A-Z]{5}\d{4}[A-Z])', re.IGNORECASE)
    fname_pattern = re.compile(
        r"Father's\s+Name\s*:?\s*(\w+\s+\w+\s+\w+)", re.IGNORECASE)
    dob_pattern = re.compile(
        r"Date\s+of\s+Birth\s+\n(\d{2}/\d{2}/\d{4})", re.IGNORECASE)



    # Search for matches using the regular expressions
    name_match = name_pattern.search(text)
    pan_match = pan_pattern.search(text)
    fname_match = fname_pattern.search(text) 
    dob_match = dob_pattern.search(text)

    if name_match:
        name = name_match.group(1)
    else:
        name = "Name not found"

    if pan_match:
        pan = pan_match.group(1)
    else:
        pan = "PAN not found"

    if fname_match:
        fname = fname_match.group(1)
    else:
        fname = "Father's name not found"

    if dob_match:
        dob = dob_match.group(1)
    else:
        dob = "Date of birth not found"



    st.write("Name:", name)
    st.write("Father's name:", fname)
    st.write("Date of Birth:", dob)
    st.write("PAN card number:", pan)



def process_passport(threshold):
     # Apply morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate = cv2.dilate(threshold, kernel, iterations=1)
    erode = cv2.erode(dilate, kernel, iterations=1)

    # Pass the preprocessed image to Tesseract OCR engine
    text = pytesseract.image_to_string(erode)

    # Split the text into lines and store them in a list
    lines = text.split('\n')
    st.write(lines)

    
    # Parse the extracted text to find the name and PAN card number using regular expressions
    passportno_pattern = re.compile(
        r"Passport\s+No\.\s+(\w\d{7})", re.IGNORECASE)
    surname_pattern = re.compile(
        r"Surname\s+(\w+)", re.IGNORECASE)
    name_pattern = re.compile(
        r"Given\s+Name\(s\)\s+(\w+)", re.IGNORECASE)
    sex_pattern = re.compile(
        r"Sex\s+(\w)", re.IGNORECASE)
    dob_pattern = re.compile(
        r"Date\s+of\s+Birth\s+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    pob_pattern = re.compile(
        r"Place\s+of\s+Birth\s+([\w\s,]+)", re.IGNORECASE)
    poi_pattern = re.compile(
        r"Place\s+of\s+Issue\s+([\w\s]+)", re.IGNORECASE)
    doi_pattern = re.compile(
        r"Date\s+of\s+Issue\s+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    doe_pattern = re.compile(
        r"Date\s+of\s+Expiry\s+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    nof_pattern = re.compile(
        r"Name\s+of\s+Father\s+([\w\s]+)", re.IGNORECASE)
    nom_pattern = re.compile(
        r"Name\s+of\s+Mother\s+([\w\s]+)", re.IGNORECASE)
    address_pattern = re.compile(
        r"Address\s*((?:.+\n)+?.*INDIA)", re.IGNORECASE)



    # Search for matches using the regular expressions
    passportno_match = passportno_pattern.search(text)
    surname_match = surname_pattern.search(text)
    name_match = name_pattern.search(text)
    sex_match = sex_pattern.search(text)
    dob_match = dob_pattern.search(text)
    pob_match = pob_pattern.search(text)
    poi_match = poi_pattern.search(text)
    doi_match = doi_pattern.search(text)
    doe_match = doe_pattern.search(text)
    nof_match = nof_pattern.search(text)
    nom_match = nom_pattern.search(text)
    address_match = address_pattern.search(text)





    if passportno_match:
        passportno = passportno_match.group(1)
    else:
        passportno = "Passport number not found"
    
    if surname_match:
        surname = surname_match.group(1)
    else:
        surname = "Surname not found"

    if name_match:
        name = name_match.group(1)
    else:
        name = "Name not found"

    if sex_match:
        sex = sex_match.group(1)
    else:
        sex = "Sex not found"

    if dob_match:
        dob = dob_match.group(1)
    else:
        dob = "Date of birth not found"

    if pob_match:
        pob = pob_match.group(1)
    else:
        pob = "Place of birth not found"

    if poi_match:
        poi = poi_match.group(1)
    else:
        poi = "Place of issue not found"

    if doi_match:
        doi = doi_match.group(1)
    else:
        poi = "Date of issue not found"

    if doe_match:
        doe = doe_match.group(1)
    else:
        doe = "Date of Expiry not found"

    if nof_match:
        nof = nof_match.group(1)
    else:
        nof = "Name of Father not found"

    if nom_match:
        nom = nom_match.group(1)
    else:
        nom = "Name of Mother not found"

    if address_match:
        address = address_match.group(1)
    else:
        address = "Address not found"
    

    st.write("Passport number:", passportno)
    st.write("Surname:", surname)
    st.write("Name:", name)
    st.write("Sex:", sex)
    st.write("Date of Birth:", dob)
    st.write("Place of Birth:", pob)
    st.write("Place of issue:", poi)
    st.write("Date of issue:", doi)
    st.write("Date of Expiry:", doe)
    st.write("Name of Father:", nof)
    st.write("Name of Mother:", nom)
    st.write("Address:", address)

if uploaded_file:

    file_extension = uploaded_file.name.split('.')[-1]
    image_extensions = accepted_file_extensions[1:]

    with st.spinner('Loading'):

        if file_extension in image_extensions:

            image = Image.open(uploaded_file)
            process_image(image)

        else:

            with io.BytesIO(uploaded_file.read()) as pdf_file:
                images = convert_from_bytes(pdf_file.read(), poppler_path=poppler_path)
                #images = convert_from_bytes(pdf_file.read())

            for i, img in enumerate(images):
                # st.image(img, caption=f'PDF page {i+1}')
                process_image(img)

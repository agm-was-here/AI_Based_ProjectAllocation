import os
# import fitz
from flask import Flask, render_template, request, redirect, url_for, flash
# from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder=r"C:\Users\aswin\OneDrive\Desktop\hack_evolve\hack_Evolve\hackathon\templates")
app.secret_key = os.urandom(24)  # Generating a random secret key

# Dummy credentials (not recommended in production)
STUDENT_USERNAME = '1234'
ADMIN_USERNAME = '123'
PASSWORD = '123'

# Create a dictionary to store form data
form_data = {
    'student': {},
    'admin': {}
}

# ocr = PaddleOCR(use_table=True, lang='en', use_gpu=False)  # Explicitly set use_gpu to False

overall_attainment_scores = {
    'frontend': 0,
    'backend': 0,
    'devops': 0,
    'data_science': 0
}

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if request.form.get('submit') == 'InternLogin' and username == STUDENT_USERNAME and password == PASSWORD:
        return redirect(url_for('registration'))
    elif request.form.get('submit') == 'AdminLogin' and username == ADMIN_USERNAME and password == PASSWORD:
        return redirect(url_for('interndetail'))
    flash('Invalid username or password', 'error')  # Flash an error message for invalid credentials
    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Extracting only the required fields from the registration form
        registration_data = {
            'name': request.form.get('name', ''),
            'dob': request.form.get('dob', ''),
            'aadhar': request.form.get('aadhar', ''),
            'pan': request.form.get('pan', '')
        }

        # Storing the extracted data in the form_data dictionary
        form_data['student'] = registration_data

        return redirect(url_for('upload'))

    return render_template('registration.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    message = None
    uploaded_files = {}

    if request.method == 'POST':
        text_fields = ['aadhar', 'pan', '10th_certificate', '12th_certificate', 'resume']

        for field in text_fields:
            file = request.files.get(field)
            if file:
                file_path = save_and_extract_text(file, field)
                uploaded_files[field] = file_path

        if request.form.get('validate') == 'Validate':
            # Perform OCR on Aadhar and PAN PDF files
            if 'aadhar' in uploaded_files:
                aadhar_text = ocr_extract_text(uploaded_files['aadhar'])
                save_text_to_file(aadhar_text, 'aadhar_text.txt')
            if 'pan' in uploaded_files:
                pan_text = ocr_extract_text(uploaded_files['pan'])
                save_text_to_file(pan_text, 'pan_text.txt')

            # Compare the extracted details with registration details
            if compare_registration_details():
                message = "Aadhar and PAN details match!"
            else:
                message = "Aadhar and PAN details do not match!"

            return render_template('submit_success.html', message=message)

        flash('Upload successful', 'success')  # Flash a success message upon successful upload

    return render_template('upload.html', uploaded_files=uploaded_files)


def save_and_extract_text(file, field_name):
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, secure_filename(file.filename))
    print("Saving file to:", file_path)  # Debug statement to check the file path
    try:
        file.save(file_path)
        print("File saved successfully!")  # Debug statement to confirm successful file saving
        return file_path
    except Exception as e:
        print("Error saving file:", str(e))  # Debug statement to print any error that occurs during file saving
        return None


def ocr_extract_text(pdf_path):
    doc = fitz.open(pdf_path)  # Open the PDF document
    text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")

    doc.close()  # Close the PDF document after extraction
    return text


def save_text_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)


def compare_registration_details():
    aadhar_pan_info = ''
    with open('aadhar_text.txt', 'r', encoding='utf-8') as aadhar_file, open('pan_text.txt', 'r',
                                                                               encoding='utf-8') as pan_file:
        aadhar_pan_info = aadhar_file.read() + pan_file.read()

    # Extract registration details
    registration_data = form_data['student']
    registration_aadhar = registration_data.get('aadhar', '')
    print(registration_aadhar)
    registration_pan = registration_data.get('pan', '')

    # Check if registration data is present in the text file
    if registration_aadhar in aadhar_pan_info and registration_pan in aadhar_pan_info:
        return True
    else:
        return False


@app.route('/submit_success')
def submit_success():
    return "Form submitted successfully!"


@app.route('/dashboard')
def dashboard():
    intern_id = request.args.get('internId')
    # Perform any necessary operations here
    return render_template('dashboard.html',overall_attainment_scores=overall_attainment_scores)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    overall_attainment_scores.update(data['overallScores'])
    return jsonify(success=True)


@app.route('/interndetail', methods=['GET', 'POST'])
def interndetail():
    return render_template('interndetail.html')


if __name__ == "__main__":
    app.run(debug=True)

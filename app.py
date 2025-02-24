import os
import pdfplumber
import spacy
import nltk
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# Initialize Flask
app = Flask(__name__)

# Load NLP Model
nlp = spacy.load("en_core_web_sm")

# Allowed file extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Sample job description
JOB_DESCRIPTION = """
We are looking for a Python Developer with experience in Flask, Machine Learning, and NLP. 
The candidate should have knowledge of APIs, database management, and cloud deployment.
"""

# Check allowed file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Resume filtering function
def filter_resume(resume_text, job_description):
    resume_doc = nlp(resume_text.lower())
    job_doc = nlp(job_description.lower())

    # Extract skills (basic method using keywords)
    skills = {"python", "flask", "machine learning", "nlp", "api", "database", "cloud"}
    resume_skills = {token.text for token in resume_doc if token.text in skills}
    
    # Calculate match percentage
    match_score = len(resume_skills) / len(skills) * 100

    return {"skills_matched": list(resume_skills), "match_score": match_score}

# Upload and process resume
@app.route("/", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            resume_text = extract_text_from_pdf(file_path)
            result = filter_resume(resume_text, JOB_DESCRIPTION)

            return jsonify(result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

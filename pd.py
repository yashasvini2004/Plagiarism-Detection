from flask import Flask, render_template, request
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Define the upload directory
UPLOAD_FOLDER = 'C:/xampp/htdocs/plagiarism'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to preprocess text
def preprocess_text(text):
    # Convert text to lowercase and remove any non-alphanumeric characters
    text = text.lower()
    text = ''.join(e for e in text if e.isalnum() or e.isspace())
    return text

# Function to compute similarity between documents
def compute_similarity(doc1, doc2):
    vectorizer = TfidfVectorizer(min_df=1)
    vectors = vectorizer.fit_transform([doc1, doc2])
    similarity = cosine_similarity(vectors)[0][1]  # changed indexing here
    return similarity

# Function to check plagiarism
def check_plagiarism(file_content, uploaded_filename):
    text1 = preprocess_text(file_content)
    plagiarism_results = []
    if text1.strip() == '':
        print("Uploaded file is empty.")
        return plagiarism_results
    print("Uploaded file content:", text1)  # Debug print
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".txt") and filename != uploaded_filename:
            with open(os.path.join(UPLOAD_FOLDER, filename), "r", encoding="utf-8") as file:
                text2 = preprocess_text(file.read())
                print("Preprocessed text:", text2)  # Debug print
                similarity_score = compute_similarity(text1, text2)
                plagiarism_results.append((uploaded_filename, filename, similarity_score))
                print(f"Comparing {uploaded_filename} with {filename}. Similarity: {similarity_score}")
    return plagiarism_results

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return render_template('index.html', error='No selected file')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        print("File size after saving:", os.path.getsize(file_path))  # Debug print
        if os.path.getsize(file_path) == 0:
            return render_template('index.html', error='Uploaded file is empty')
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        plagiarism_results = check_plagiarism(file_content, uploaded_file.filename)
        return render_template('result.html', plagiarism_results=plagiarism_results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import traceback
import os

from mediscan import analyze_with_gemini

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        raw_bytes = file.read()
        is_pdf = file.filename.lower().endswith('.pdf')
        
        # Analyze using the existing mediscan logic
        result = analyze_with_gemini(raw_bytes, context="", is_pdf=is_pdf)
        return jsonify(result)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

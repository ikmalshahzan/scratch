# MediScan Local Web App

MediScan is an AI-powered medical diagnostic suite that uses Google's Gemini models to analyze medical scans and generate diagnoses, anatomical body maps, and tailored exercise plans.

This repository contains a local web interface built with Python (Flask) and a modern HTML/CSS frontend to easily test the application.

## 🚀 Local Setup Instructions

### 1. Prerequisites
- **Python 3**
- A **Gemini API Key** (Note: Image and Video generation features require a paid/billing-enabled Gemini API tier. The textual diagnosis works on the free tier).

### 2. Installation
1. Clone the repository or download the files.
2. Open a terminal in the project folder.
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Variables (API Key)
For security, the API key is safely loaded from environment variables rather than hardcoded.
1. Create a file named `.env` in the root folder of the project.
2. Add your Gemini API key to the `.env` file like this:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
*(Note: `.env` is intentionally ignored by `.gitignore` so your key will never be accidentally uploaded to GitHub).*

### 4. Running the Web App
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to: `http://localhost:5000`
3. Drag and drop a medical scan image or PDF to view the AI diagnosis!

---

## 🐙 How to Push to GitHub

If you want to push updates to this project to your GitHub repository, follow these steps in your terminal:

1. **Initialize Git** (if you haven't already):
   ```bash
   git init
   ```
2. **Stage Your Files**:
   ```bash
   git add .
   ```
3. **Commit Your Changes**:
   ```bash
   git commit -m "Update MediScan App"
   ```
4. **Link Your GitHub Repository** (if you haven't linked it yet):
   ```bash
   git branch -M main
   git remote add origin https://github.com/ikmalshahzan/scratch.git
   ```
5. **Push the Code**:
   ```bash
   git push -u origin main
   ```
   *A GitHub login window may pop up. Sign in to authenticate and complete the push.*

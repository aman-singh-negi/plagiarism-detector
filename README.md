# Plagiarism Detection System

A comprehensive plagiarism detection tool for both text and code files.

## Features
- Text similarity analysis (Jaccard, Cosine, Levenshtein, MinHash)
- Code structure comparison (Python, Java, C++)
- Interactive heatmap visualization
- Dark/light mode toggle
- PDF report generation

## Installation
1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
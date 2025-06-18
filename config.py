import os

class Config:
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'py', 'java', 'cpp', 'c', 'h'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Analysis settings
    MINHASH_PERMUTATIONS = 128
    HEATMAP_WINDOW_SIZE = 100
    MIN_MATCH_LENGTH = 50
    
    # PDF report settings
    REPORT_TITLE = "Plagiarism Analysis Report"
    REPORT_AUTHOR = "Plagiarism Detector"
    
    # Create required directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
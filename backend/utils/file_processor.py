import os
import PyPDF2
import docx
from bs4 import BeautifulSoup
from config import Config
import sys
class FileProcessor:
    def __init__(self):
        pass
    def process_files(self, file1, file2):
        if not (self._allowed_file(file1.filename) and self._allowed_file(file2.filename)):
            raise ValueError("Unsupported file type")
        
        ext1 = os.path.splitext(file1.filename)[1].lower()
        ext2 = os.path.splitext(file2.filename)[1].lower()
        
        if ext1 != ext2:
            # If file types differ, treat both as text
            file_type = 'text'
        else:
            file_type = self._get_file_type(ext1)
        
        content1 = self._read_file(file1, ext1)
        content2 = self._read_file(file2, ext2)
        
        return content1, content2, file_type
    
    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    def _get_file_type(self, extension):
        mapping = {
            '.py': 'python',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp'
        }
        return mapping.get(extension, 'text')
    
    def _read_file(self, file, extension):
        if extension == '.pdf':
            return self._read_pdf(file)
        elif extension == '.docx':
            return self._read_docx(file)
        elif extension in ('.txt', '.html'):
            return file.read().decode('utf-8')
        elif extension in ('.py', '.java', '.cpp'):
            return file.read().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
    
    def _read_pdf(self, file):
        text = ""
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    
    def _read_docx(self, file):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
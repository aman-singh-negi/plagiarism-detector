import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from similarity.text_analyzer import TextAnalyzer
from similarity.code_analyzer import CodeAnalyzer
from utils.file_processor import FileProcessor
from utils.report_generator import ReportGenerator
from datetime import datetime
from config import Config

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates'))
app = Flask(__name__, template_folder=template_dir)
#app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

text_analyzer = TextAnalyzer()
code_analyzer = CodeAnalyzer()
file_processor = FileProcessor()
report_generator = ReportGenerator()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'Please upload both files'}), 400
            
        file1, file2 = request.files['file1'], request.files['file2']
        
        content1, content2, file_type = file_processor.process_files(file1, file2)
        
        if file_type in ('python', 'java', 'cpp'):
            results = code_analyzer.compare(content1, content2, file_type)
        else:
            results = text_analyzer.compare(content1, content2)
        
        return jsonify({
            'success': True,
            'results': results,
            'file1_name': file1.filename,
            'file2_name': file2.filename,
            'file1_preview': content1[:500] + ('...' if len(content1) > 500 else ''),
            'file2_preview': content2[:500] + ('...' if len(content2) > 500 else ''),
            'timestamp': datetime.now().isoformat(),
            'type': file_type
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.json
        pdf_path = report_generator.generate(data)
        return send_from_directory(os.path.dirname(pdf_path), os.path.basename(pdf_path), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
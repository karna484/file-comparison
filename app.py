from flask import Flask, render_template, request, jsonify
from comparison import compare_folder_contents
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare_folder', methods=['POST'])
def compare_folder():
    if 'files' not in request.files:
        return jsonify({'error': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({'error': 'No files uploaded'}), 400
    
    file_paths = []
    try:
        for file in files:
            if file.filename == '':
                continue
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        if len(file_paths) < 2:
            return jsonify({'error': 'Need at least 2 valid files to compare'}), 400
        
        results = compare_folder_contents(file_paths)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)

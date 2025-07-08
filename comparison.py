import difflib
from collections import defaultdict
import os
from PyPDF2 import PdfReader
from docx import Document
import textract
from PIL import Image
import pytesseract

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Error reading DOCX {docx_path}: {str(e)}")

def extract_text_from_doc(doc_path):
    try:
        text = textract.process(doc_path)
        return text.decode('utf-8', errors='ignore')
    except Exception as e:
        raise Exception(f"Error reading DOC {doc_path}: {str(e)}")

def extract_text_from_png(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise Exception(f"Error reading PNG {image_path}: {str(e)}")

def read_file_content(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.txt':
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext == '.docx':
        return extract_text_from_docx(path)
    elif ext == '.doc':
        return extract_text_from_doc(path)
    elif ext == '.png':
        return extract_text_from_png(path)
    else:
        raise Exception(f"Unsupported file type: {ext}")

def compare_folder_contents(file_paths):
    try:
        # Read all files using proper handlers
        file_contents = {}
        for path in file_paths:
            file_contents[os.path.basename(path)] = read_file_content(path)
        
        # Compare all pairs
        similarity_matrix = defaultdict(dict)
        all_matches = defaultdict(list)
        filenames = list(file_contents.keys())
        
        for i in range(len(filenames)):
            for j in range(i+1, len(filenames)):
                file1 = filenames[i]
                file2 = filenames[j]
                text1 = file_contents[file1]
                text2 = file_contents[file2]
                
                # Calculate similarity
                matcher = difflib.SequenceMatcher(None, text1, text2)
                similarity = round(matcher.ratio() * 100, 2)
                similarity_matrix[file1][file2] = similarity
                similarity_matrix[file2][file1] = similarity
                
                # Find matching blocks
                for block in matcher.get_matching_blocks():
                    if block.size > 10:
                        match_text = text1[block.a:block.a+block.size]
                        all_matches[match_text].append((file1, file2))
        
        # Prepare highlighted results
        highlighted_results = []
        for match_text, files in all_matches.items():
            if len(files) > 1:
                file_list = ", ".join(set(f"{f1} and {f2}" for f1, f2 in files))
                highlighted_results.append({
                    'text': match_text,
                    'files': file_list,
                    'count': len(set(f for pair in files for f in pair))
                })
        
        # Sort by most common matches
        highlighted_results.sort(key=lambda x: (-x['count'], x['text']))
        
        return {
            'similarity_matrix': similarity_matrix,
            'common_matches': highlighted_results,
            'total_files': len(filenames)
        }

    except Exception as e:
        raise Exception(f"Error comparing folder contents: {str(e)}")

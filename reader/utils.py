import fitz, docx2txt

def read_file(file_path, file_name):
    if file_name.lower().endswith('.pdf'):
        # doc = fitz.open(file_path)
        content = ''.join(page.get_text() for page in fitz.open(file_path))
    elif file_name.lower().endswith('.docx'):
        try:
            content = docx2txt.process(file_path)
        except Exception as e:
            return None
    else:
        # Unsupported file format
        return None
    
    return content
from pdfminer.high_level import extract_text

def read_text(txt):
    with open(txt, 'r') as file: 
        data = file.read().replace('\n', '')
        return data

def extract_resume(file):
    text = extract_text(file)
    return text
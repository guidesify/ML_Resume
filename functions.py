def read_text(txt):
    with open(txt, 'r') as file: 
        data = file.read().replace('\n', '')
        return data

def extract_resume(file):
    from pdfminer.high_level import extract_text
    text = extract_text(file)
    return text
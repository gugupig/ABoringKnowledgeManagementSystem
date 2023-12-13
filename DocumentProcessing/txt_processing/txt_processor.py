# txt_processor.py

def extract_text_from_txt(txt_path):
    text = {}
    with open(txt_path, 'r') as file:
        text[1] = file.read()
    return text

if __name__ == "__main__":
    pass

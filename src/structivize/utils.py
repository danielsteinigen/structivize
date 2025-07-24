import json
import os


def load_json(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(filename: str):
    with open(filename, "r") as json_file:
        return [json.loads(line) for line in json_file]


def save_json(filename: str, data: dict):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_jsonl(filename: str, data: list):
    with open(filename, "a", encoding="utf-8") as f:
        for sample in data:
            f.write(f"{json.dumps(sample, ensure_ascii=False)}\n")


def load_text(filename: str):
    with open(filename) as text_file:
        return text_file.read()


def save_text(filename: str, data: str):
    with open(filename, "w") as text_file:
        text_file.write(data)


def save_bytes(filename: str, data: str):
    with open(filename, "wb") as binary_file:
        binary_file.write(data)


def check_dirs(path: str):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def insert_line(path: str, line: str):
    with open(path, "r") as file:
        content = file.read()

    with open(path, "w") as file:
        file.write(line + content)


def remove_files(path: str, endings: list = [""]):
    for ext in endings:
        try:
            if ext != "":
                os.remove(f"{path}.{ext}")
            else:
                os.remove(path)
        except:
            pass


def remove_files_dir(path: str, endings: list):
    for f in os.listdir(path):
        for ext in endings:
            if f.endswith(f".{ext}"):
                os.remove(os.path.join(path, f))


def extract_part(text, term_1, term_2, return_empty, remove_first_line=False):
    text_result = "" if return_empty else text
    offset = len(term_1)
    start_code = text.find(term_1)

    if start_code != -1:
        if term_2 != "":
            end_code = text.find(term_2, start_code + offset)
            if end_code != -1:
                if remove_first_line:
                    text_result = text[start_code:end_code]
                    text_result = "\n".join(text_result.split("\n")[1:])
                else:
                    text_result = text[start_code + offset : end_code]
            else:
                if remove_first_line:
                    text_result = ""  # if code is incomplete, return empty string
                    # text_result = text[start_code:]
                    # text_result = "\n".join(text_result.split("\n")[1:])
                else:
                    text_result = text[start_code + offset :]
        else:
            text_result = text[start_code + offset :]

    return text_result.strip()

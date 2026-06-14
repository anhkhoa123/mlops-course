import csv

def load_csv(file_path: str) -> list:
    """
    Doc file CSV va tra ve danh sach cac dong du lieu.
    file_path : duong dan den file CSV can doc
    """
    rows = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"Da doc {len(rows)} dong tu {file_path}")
    return rows

def load_txt(file_path: str) -> list:
    """
    Doc file TXT, moi dong la mot phan tu trong danh sach.
    """
    with open(file_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    print(f"Da doc {len(lines)} dong tu {file_path}")
    return lines

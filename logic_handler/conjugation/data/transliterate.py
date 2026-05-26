import csv
import os

# --- SLP1 -> IAST mapping ---
SLP1_TO_IAST = {
    # vowels
    "a": "a", "A": "ā", "i": "i", "I": "ī",
    "u": "u", "U": "ū", "f": "ṛ", "F": "ṝ",
    "x": "ḷ", "X": "ḹ",
    "e": "e", "E": "ai",
    "o": "o", "O": "au",

    # consonants
    "k": "k", "K": "kh", "g": "g", "G": "gh", "N": "ṅ",
    "c": "c", "C": "ch", "j": "j", "J": "jh", "Y": "ñ",
    "w": "ṭ", "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ",
    "t": "t", "T": "th", "d": "d", "D": "dh", "n": "n",
    "p": "p", "P": "ph", "b": "b", "B": "bh", "m": "m",

    # semivowels + sibilants
    "y": "y", "r": "r", "l": "l", "v": "v",
    "S": "ś", "z": "ṣ", "s": "s", "h": "h",

    # special
    "M": "ṃ", "H": "ḥ", "~": "̃"
}

# Columns we want to transliterate
TARGET_COLUMNS = {
    "result"
}


def slp1_to_iast(text: str) -> str:
    """Convert SLP1 string to IAST."""
    result = []
    for char in text:
        result.append(SLP1_TO_IAST.get(char, char))  # fallback = keep char
    return "".join(result)


def process_csv(input_path, output_path):
    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames.copy()

        # Add new IAST columns
        new_fields = []
        for col in fieldnames:
            if col in TARGET_COLUMNS:
                new_fields.append(col + "_IAST")

        fieldnames.extend(new_fields)

        rows = []
        for row in reader:
            for col in TARGET_COLUMNS:
                if col in row and row[col]:
                    row[col + "_IAST"] = slp1_to_iast(row[col])
            rows.append(row)

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            in_path = os.path.join(input_folder, filename)
            out_path = os.path.join(output_folder, filename)

            print(f"Processing {filename}...")
            process_csv(in_path, out_path)


if __name__ == "__main__":
    INPUT_DIR = "data/"
    OUTPUT_DIR = "output_csvs"

    process_folder(INPUT_DIR, OUTPUT_DIR)
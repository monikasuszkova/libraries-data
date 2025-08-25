import sys
import unicodedata

# Replacement map for “fancy” characters not present in ASCII
REPLACE = {
    '–': '-', '—': '-', '‒': '-', 
    '“': '"', '”': '"', '„': '"', '«': '"', '»': '"',
    '‘': "'", '’': "'", '‚': "'", '´': "'", '`': "'",
    '…': '...', '•': '-', '·': '-',
    '№': 'No.', '§': 'S', '×': 'x', '÷': '/',
    '\u00A0': ' ',  # non-breaking space -> normal space
}

def strip_diacritics(s: str) -> str:
    # Normalize (NFKD) and remove combining diacritics
    n = unicodedata.normalize('NFKD', s)
    return ''.join(ch for ch in n if not unicodedata.combining(ch))

def clean_to_ascii(s: str) -> str:
    # Replace fancy characters with ASCII equivalents
    s = s.translate({ord(k): v for k, v in REPLACE.items()})
    # Remove diacritics (č->c, ř->r, ů->u, etc.)
    s = strip_diacritics(s)
    # Make sure only pure ASCII remains
    return s.encode('ascii', 'ignore').decode('ascii')

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 convert_to_ascii.py <input_file> <output_file>")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]

    # Use newline='' to preserve CSV formatting
    with open(input_file, 'r', encoding='utf-8', newline='') as fi, \
         open(output_file, 'w', encoding='ascii', newline='') as fo:
        for line in fi:
            fo.write(clean_to_ascii(line))

    print(f"Conversion complete. Saved to: {output_file}")

if __name__ == "__main__":
    main()

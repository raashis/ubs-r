from flask import request, jsonify, Blueprint

trivia_bp = Blueprint('trivia', __name__)

# Map for number word detection
import re

# English number word parser
from word2number import w2n

import roman

def roman_to_int(s):
    return roman.fromRoman(s)


# Language tags for sorting (used in Part TWO)
LANGUAGE_PRIORITY = {
    'roman': 0,
    'english': 1,
    'traditional_chinese': 2,
    'simplified_chinese': 3,
    'german': 4,
    'arabic': 5
}

ROMAN_NUMERAL_MAP = {
    'M': 1000,
    'CM': 900,
    'D': 500,
    'CD': 400,
    'C': 100,
    'XC': 90,
    'L': 50,
    'XL': 40,
    'X': 10,
    'IX': 9,
    'V': 5,
    'IV': 4,
    'I': 1
}

GERMAN_NUMBERS = {
    "null": 0, "eins": 1, "eine": 1, "ein": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5,
    "sechs": 6, "sieben": 7, "acht": 8, "neun": 9, "zehn": 10, "elf": 11, "zwölf": 12,
    "dreizehn": 13, "vierzehn": 14, "fünfzehn": 15, "sechzehn": 16, "siebzehn": 17,
    "achtzehn": 18, "neunzehn": 19, "zwanzig": 20, "dreißig": 30, "vierzig": 40, "fünfzig": 50,
    "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90, "hundert": 100, "tausend": 1000
}

@trivia_bp.route('/duolingo-sort', methods=['POST'])
def duolingo_sort():
    data = request.get_json()
    part = data.get('part')
    unsorted_list = data.get('challengeInput', {}).get('unsortedList', [])

    if part == 'ONE':
        result = part_one(unsorted_list)
    elif part == 'TWO':
        result = part_two(unsorted_list)
    else:
        return jsonify({'error': 'Invalid part'}), 400

    return jsonify({'sortedList': result})


def roman_to_int(s):
    i = 0
    num = 0
    while i < len(s):
        if i + 1 < len(s) and s[i:i+2] in ROMAN_NUMERAL_MAP:
            num += ROMAN_NUMERAL_MAP[s[i:i+2]]
            i += 2
        else:
            num += ROMAN_NUMERAL_MAP[s[i]]
            i += 1
    return num


def detect_language_and_parse(value):
    stripped = value.strip()
    
    # Check Arabic digits
    if stripped.isdigit():
        return int(stripped), 'arabic'

    # Check Roman
    try:
        return roman_to_int(stripped), 'roman'
    except:
        pass

    # English (try word2number)
    try:
        num = w2n.word_to_num(stripped.lower())
        return num, 'english'
    except:
        pass

    # German
    try:
        german_num = german_to_int(stripped.lower())
        if german_num is not None:
            return german_num, 'german'
    except:
        pass

    # Traditional/Simplified Chinese (assuming < 100000)
    try:
        from cn2an import cn2an
        num = cn2an.cn2an(stripped, "smart")
        if contains_traditional_chinese(stripped):
            return num, 'traditional_chinese'
        else:
            return num, 'simplified_chinese'
    except:
        pass

    return float('inf'), 'unknown'  # fallback


def contains_traditional_chinese(s):
    # Crude check using Unicode ranges
    return any('\u4e00' <= ch <= '\u9fff' for ch in s)


def german_to_int(text):
    # Use regex to split compound words
    text = text.replace("und", "")
    for word, value in GERMAN_NUMBERS.items():
        text = text.replace(word, f' {value} ')
    numbers = [int(n) for n in re.findall(r'\b\d+\b', text)]
    return sum(numbers) if numbers else None


def part_one(unsorted_list):
    values = []
    for item in unsorted_list:
        if item.isdigit():
            values.append((int(item), str(int(item))))
        else:
            val = roman_to_int(item)
            values.append((val, str(val)))

    values.sort(key=lambda x: x[0])
    return [v[1] for v in values]


def part_two(unsorted_list):
    parsed = []

    for item in unsorted_list:
        num, lang = detect_language_and_parse(item)
        parsed.append((num, LANGUAGE_PRIORITY.get(lang, 999), lang, item))

    parsed.sort(key=lambda x: (x[0], x[1]))
    return [x[3] for x in parsed]

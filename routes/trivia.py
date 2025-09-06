from flask import Blueprint, request, jsonify
import roman  # reliable Roman numeral parsing
from word2number import w2n  # robust English parsing
from cn2an import cn2an  # versatile Chinese parsing
from number_parser import parse_number  # advanced German parsing
import re

trivia_bp = Blueprint('trivia', __name__)

LANGUAGE_PRIORITY = {
    'roman': 0,
    'english': 1,
    'traditional_chinese': 2,
    'simplified_chinese': 3,
    'german': 4,
    'arabic': 5
}

def detect_language_and_parse(value: str):
    s = value.strip()
    
    # Arabic numerals
    if s.isdigit():
        return int(s), 'arabic'

    # Roman numerals
    try:
        return roman.fromRoman(s.upper()), 'roman'
    except Exception:
        pass

    # English words
    try:
        num = w2n.word_to_num(s.lower().replace('-', ' '))
        return num, 'english'
    except Exception:
        pass

    # German numbers using number-parser
    try:
        parsed = parse_number(s, language="de")
        if parsed is not None:
            return int(parsed), 'german'
    except Exception:
        pass

    # Chinese numbers
    try:
        num = cn2an.cn2an(s, "smart")
        if any('\u4e00' <= ch <= '\u9fff' for ch in s):
            # Heuristic for Traditional vs Simplified Chinese
            if any(trad in s for trad in ['萬', '億', '壹', '貳', '參']):
                return num, 'traditional_chinese'
            else:
                return num, 'simplified_chinese'
    except Exception:
        pass

    # Fallback: parsing failed
    return float('inf'), 'unknown'


@trivia_bp.route('/duolingo-sort', methods=['POST'])
def duolingo_sort():
    data = request.get_json()
    part = data.get('part')
    unsorted = data.get('challengeInput', {}).get('unsortedList', [])

    if part == 'ONE':
        sorted_list = []
        for x in unsorted:
            val = int(x) if x.isdigit() else roman.fromRoman(x)
            sorted_list.append((val, str(val)))
        sorted_list.sort(key=lambda p: p[0])
        result = [s for _, s in sorted_list]

    elif part == 'TWO':
        parsed = [
            (*detect_language_and_parse(x), x)
            for x in unsorted
        ]

        # Uncomment for debugging:
        # import json
        # print(json.dumps(parsed, indent=2, ensure_ascii=False))

        parsed.sort(key=lambda t: (t[0], LANGUAGE_PRIORITY.get(t[1], 999)))
        result = [orig for _, _, orig in parsed]

    else:
        return jsonify({'error': 'Part must be "ONE" or "TWO"'}), 400

    return jsonify({'sortedList': result})

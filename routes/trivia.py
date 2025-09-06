# routes/trivia.py

from flask import Blueprint, jsonify

trivia_bp = Blueprint('trivia', __name__)

@trivia_bp.route('/trivia', methods=['GET'])
def trivia():
    answers = [
        3, 1, 2, 2, 3,
        4, 4, 5, 4, 3,
        3, 2, 2, 1, 2,
        3, 1
    ]
    return jsonify({"answers": answers})

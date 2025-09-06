from flask import jsonify
from routes import app

@app.route('/trivia', methods=['GET'])
def trivia():
    answers = [
        3, #need to see again
        1,
        2, 
        2,  
        3,
        4, 
        4,  
        5,  # 8. Capture The Flag -> 2
        4,  # 9. Filler 1 -> 2
        3,  # 10. Trading Formula -> 1
        3,  # 11. Filler (Encore) -> 1
        2,  # 12. Chase The Flag -> 2
        2,  # 13. Snakes and Ladders Power Up! -> 2
        1,  # 14. The Ink Archive -> 1
        2,  # 15. CoolCode Hacker -> 2
        3,  # 16. Fog-of-Wall -> 1
        1   # 17. Filler 2 -> 1
    ]
    return jsonify({"answers": answers})

import json
import logging
import pandas as pd
from flask import request
from routes import app

logger = logging.getLogger(__name__)

def impute_series(series):
    s = pd.Series(series, dtype="float")
    # Linear interpolation + fill edges
    s = s.interpolate(method='linear', limit_direction='both')
    return s.tolist()

@app.route('/blankety', methods=['POST'])
def impute():
    data = request.get_json()
    logger.info("Received data for imputation")
    series_list = data.get("series", [])
    
    imputed = [impute_series(s) for s in series_list]
    
    logger.info("Imputation complete")
    return json.dumps({"answer": imputed})

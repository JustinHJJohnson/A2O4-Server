from flask import Flask, request
from flask_cors import CORS
import re
import sqlite
import ao3

host = '192.168.1.2'
app = Flask(__name__)
CORS(app)

@app.route('/ao3Download', methods=['POST'])
def download_work_or_series():
    if request.method == 'POST':
        url = request.json["url"]
        results = re.findall(r"(series|works)\/(\d{6,8})", url)[0]
        error = False
        if (len(results) != 2):
            error = True
        elif (results[0] == "works"):
            print(f"Work with the ID: {results[1]}")
            ao3.download_work(int(results[1]))
        elif (results[0] == "series"):
            print(f"Series with the ID: {results[1]}")
            ao3.download_series(int(results[1]))
        else:
            error = True
        if (error):  return "Not a valid AO3 URL", 400
        else: return "", 200
    else:
        return "", 400

sqlite.create_database()
app.run(host=host, port=5001, debug=True)
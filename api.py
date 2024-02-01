from flask import Flask, request
from flask_cors import CORS
import re
import toml
from AO3LS import sqlite, ao3, common

host = '192.168.1.2'
app = Flask(__name__)
CORS(app)

config = common.Config(toml.load(f"./config.toml"))

@app.route('/ao3Download', methods=['POST'])
def download_work_or_series():
    if request.method == 'POST':
        url = request.json["url"]
        results = re.findall(r"(series|works)\/(\d{6,8})", url)[0]
        if (len(results) != 2):
            return "Not a valid AO3 URL", 400
        elif (results[0] == "works"):
            print(f"Work with the ID: {results[1]}")
            ao3.download_work(int(results[1]))
        elif (results[0] == "series"):
            print(f"Series with the ID: {results[1]}")
            ao3.download_series(int(results[1]))
        
        return f"Successfully downloaded work {results[1]}", 200
    else:
        return "", 400

sqlite.create_database()
app.run(host=host, port=5001, debug=True)
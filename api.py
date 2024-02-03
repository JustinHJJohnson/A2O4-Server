from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from AO3LS import sqlite, ao3, config
import AO3T as AO3

host = '192.168.1.2'
app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_work_or_series():
    if request.method == 'POST':
        url = request.json["url"]
        results = re.findall(r"(series|works)\/(\d{6,8})", url)[0]
        if (len(results) != 2):
            return "Not a valid AO3 URL", 400
        elif (results[0] == "works"):
            print(f"Work with the ID: {results[1]}")
            try:
                work_name = ao3.download_work(int(results[1]))
            except AO3.utils.InvalidIdError:
                return f"Could not find a work with the id {results[1]}", 400
            return f"Successfully downloaded work {results[1]} - {work_name}", 200
        elif (results[0] == "series"):
            print(f"Series with the ID: {results[1]}")
            try:
                series_name = ao3.download_series(int(results[1]))
            except AO3.utils.InvalidIdError:
                return f"Could not find a series with the id {results[1]}", 400
            return f"Successfully downloaded series {results[1]} - {series_name}", 200
        
@app.route('/config', methods=['GET', 'PUT'])
def get_or_update_config():
    if request.method == 'GET':
        return jsonify(config.get_config().to_json_dict())
    elif request.method == 'PUT':
        config.update_config(config.Config(request.json))
        return "Successfully updated config", 200

sqlite.create_database()
app.run(host=host, port=5001, debug=True)
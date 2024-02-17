from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import paramiko
from A2O4 import sqlite, ao3, config
import AO3T as AO3

host = '192.168.1.2'
app = Flask(__name__)
CORS(app)


@app.errorhandler(paramiko.SSHException)
def handle_bad_request(e):
    error_str = f"{e}. Make sure the device is turned on and connected to the network"
    return error_str, 503

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
                work = ao3.download_work(int(results[1]))
            except AO3.utils.InvalidIdError:
                return f"Could not find a work with the id {results[1]}", 400
            response_message = f"Successfully downloaded work {work.title}"
            if (work.series):
                response_message += f", part of series {work.series[0]}"
            response_message += f"\nin fandom(s): {ao3.map_and_filter_fandoms(work.fandoms)}"
            return response_message, 200
        elif (results[0] == "series"):
            print(f"Series with the ID: {results[1]}")
            try:
                series = ao3.download_series(int(results[1]))
            except AO3.utils.InvalidIdError:
                return f"Could not find a series with the id {results[1]}", 400
            return f"Successfully downloaded series {series.name}\nin fandom(s): {ao3.map_and_filter_fandoms(work.fandoms)}", 200
        
@app.route('/delete/<string:type>/<string:id>', methods=['DELETE'])
def delete_work_or_series(type: str, id: str):
    if (type != 'series' and type != 'work'):
        return "Can only delete a series or a work", 400
    if (not re.fullmatch(r"(\d{6,8})", id)):
        return "Not a valid id", 400
    if (type == 'work'):
        ao3.delete_work(id)
    else:
        ao3.delete_series(id)
    return "", 200
        
@app.route('/config', methods=['GET', 'PUT'])
def get_or_update_config():
    if request.method == 'GET':
        return jsonify(config.get_config().to_json_dict())
    elif request.method == 'PUT':
        config.update_config(config.Config(request.json))
        return "Successfully updated config", 200

sqlite.create_database()
app.run(host=host, port=5001, debug=True)
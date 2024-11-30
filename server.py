from flask import Flask, request, jsonify, render_template
from armod_decryptor import process_config
from netmod_decryptor import decrypt_file
from sockshttp_decryptor import file_sockshttp
#from opentunnel_decryptor import tnl_decryptor

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json()
    encrypted_content = data.get('encryptedContent')
    if not encrypted_content:
        return jsonify({'result': 'No encrypted content provided'}), 400
    try:
        result = process_config(encrypted_content)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'result': f'Error: {str(e)}'}), 500

@app.route('/decrypt-file', methods=['POST'])
def decrypt_file_route():
    data = request.get_json()
    file_content = data.get('fileContent')
    if not file_content:
        return jsonify({'result': 'No file content provided'}), 400
    try:
        result = decrypt_file(file_content)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'result': f'Error: {str(e)}'}), 500

@app.route('/file_sockshttp', methods=['POST'])
def decrypt_sockshttp_file_route():
    data = request.get_json()
    file_content = data.get('fileContent')
    if not file_content:
        return jsonify({'result': 'No file content provided'}), 400
    try:
        result = file_sockshttp(file_content)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'result': f'Error: {str(e)}'}), 500
    
'''@app.route('/file_opentunnel', methods=['POST'])
def decrypt_sockshttp():
    data = request.get_json()
    file_content = data.get('fileContent')
    if not file_content:
        return jsonify({'result': 'No file content provided'}), 400
    try:
        result = tnl_decryptor(file_content)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'result': f'Error: {str(e)}'}), 500'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

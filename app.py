import os

from flask import Flask, render_template, request, flash, jsonify, send_file, after_this_request
from flask_dropzone import Dropzone

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM = True,
    DROPZONE_MAX_FILE_SIZE = 1,
    DROPZONE_FILE_TOO_BIG="That file is too large. 1mb max...",
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*, .pdf, .txt, .torrent',
    DROPZONE_MAX_FILES=30
)

dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        message = f"{f.filename} has been succesfully uploaded 👌🏼"
        return render_template('index.html', status=message)
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/api/get')
def download_file():
    if request.method == "GET":
        
        filename = request.json.get("filename", None)
        if filename is not None:
            full_path = os.path.join(app.config['UPLOADED_PATH'], filename)
            if os.path.isfile(full_path) is True:
                
                # Allows us to delete a file AFTER this request completes...
                @after_this_request
                def remove_file(response):
                    os.remove(full_path)
                    return response

                return send_file(full_path, as_attachment=True)
            else:
                return jsonify({"error": "that file doesnt exist"})
       
        return jsonify({"error": "filename k/v pair not found"})
        




@app.route('/api/files')
def grab_file():
    if request.method == "GET":
        files = os.listdir(os.path.join(app.root_path, app.config['UPLOADED_PATH']))
        return jsonify(files)


if __name__ == '__main__':
    app.run(debug=True)
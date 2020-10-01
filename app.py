import os, json
from flask import Flask, render_template, request, flash, jsonify, send_file, after_this_request, abort
from flask_dropzone import Dropzone

# Find the upload path
basedir = os.path.abspath(os.path.dirname(__file__))

api_key_list = os.getenv("KEYS", None)
if api_key_list is None:
    print("We weren't able to load the API keys. Good luck getting in...")
else:
    parsed_key_list = json.loads(api_key_list)


def validate_key(request):
    requested_key = request.json.get("key", None)
    print(request)
    if requested_key is not None:
        if requested_key in parsed_key_list:
            return True, {}
        else:
            return False, {"err": "bad api key"}
    else:
        return False, {"err": "no api key"}

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # set secret key
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM = True, # Allows for custom file types (ie; torrent files)
    DROPZONE_MAX_FILE_SIZE = 1, # 1mb file size
    DROPZONE_FILE_TOO_BIG="That file is too large. 1mb max...", # bad boy
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*, .pdf, .txt, .torrent',
    DROPZONE_MAX_FILES=30 # num of max files
)

dropzone = Dropzone(app) # init upload field



@app.route('/', methods=['POST', 'GET'])
def upload():
    # If post, that means someone added files, put them in the correct dir...
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))

        return render_template('index.html')
    # if get, means they just tryinig to see home page...
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/api/get')
def download_file():
    if request.method == "GET": 
        
        validation_result, validation_message = validate_key(request)
        if validation_result is False:
            return jsonify(validation_message), 401
            
        # grab filename from json payload. If !filename ret err
        filename = request.json.get("filename", None)
        if filename is not None:

            full_path = os.path.join(app.config['UPLOADED_PATH'], filename) # make full path
            
            if os.path.isfile(full_path) is True: # validate file exists.
                
                # Allows us to delete a file AFTER this request completes...
                @after_this_request
                def remove_file(response):
                    os.remove(full_path) # remove the file after it's downloaded so we don't download multiple times.
                    return response

                return send_file(full_path, as_attachment=True)
            # if no file, ret err
            else:
                return jsonify({"error": "that file doesnt exist"})
        
        return jsonify({"error": "filename k/v pair not found"})
        



@app.route('/api/files')
def grab_file():
    if request.method == "GET":
        validation_result, validation_message = validate_key(request)
        if validation_result is False:
            return jsonify(validation_message), 401
        # list all of the files in the upload path so client can dl with /api/get
        files = os.listdir(os.path.join(app.root_path, app.config['UPLOADED_PATH']))
        return jsonify(files)

# debugging stuff...
if __name__ == '__main__':
    app.run(debug=True)
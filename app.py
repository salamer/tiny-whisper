from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3'}


def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/transcribe", methods=['POST'])
def transcribe():
    from faster_whisper import WhisperModel
    model_size = "tiny"
    model = WhisperModel(model_size, device="cpu", compute_type="int8",
                         download_root="/tmp", local_files_only=True)

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect("/")

    if not file or not allowed_file(file.filename):
        flash("file type is not allowed")
        return redirect("/")

    filename = secure_filename(file.filename)

    # data = file.read()

    segments, info = model.transcribe(file, beam_size=5)
    res = []
    for segment in segments:
        res.append("[%.2fs -> %.2fs] %s" %
                   (segment.start, segment.end, segment.text))

        rest = "Detected language '%s' with probability %f" % (
            info.language, info.language_probability)
    return rest + "<br>" + "<br>".join(res)


@app.route("/", methods=['GET'])
def index():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data action="/transcribe">
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def list_files(startpath):
    tree = []
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append(
            '{}{}/'.format(indent, os.path.basename(root))
        )
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree.append(
                '{}{}'.format(subindent, f)
            )
        for d in dirs:
            inside = list_files(
                os.path.join(startpath, d)
            )
            for i in inside:
                tree.append(
                    '{}{}/'.format(indent, i)
                )
    return tree

@app.route("/lookup")
def lookup():
    tree = list_files("/tmp")
    return jsonify(tree)

if __name__ == '__main__':
    app.run(debug=True, port=8000)

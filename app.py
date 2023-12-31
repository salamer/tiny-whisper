from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from distutils.dir_util import copy_tree
# import logging
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3'}


def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# TODO: make a bootstrap script, use bash to move folder


def move_file():
    target = "/tmp/models--guillaumekln--faster-whisper-tiny"
    target_tmp = "/tmp"
    src = "/app/models--guillaumekln--faster-whisper-tiny"
    if os.path.isdir(src):
        if not os.path.isdir(target):
            copy_tree(
                src,
                target_tmp,
            )


@app.route("/transcribe", methods=['POST'])
def transcribe():
    print("start")
    # move_file()
    from faster_whisper import WhisperModel
    model_size = "tiny"
    model = WhisperModel(model_size, device="cpu", compute_type="int8",
                         download_root="/tmp")
    print("finish load")
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
    print("start transcribe")
    segments, info = model.transcribe(file, beam_size=5)
    res = []
    for segment in segments:
        res.append("[%.2fs -> %.2fs] %s" %
                   (segment.start, segment.end, segment.text))

        rest = "Detected language '%s' with probability %f" % (
            info.language, info.language_probability)

    return rest + "<br>" + "<br>".join(res)


@app.route("/transcribe_json", methods=['POST'])
def transcribe_json():
    # move_file()
    from faster_whisper import WhisperModel
    model_size = "tiny"
    model = WhisperModel(model_size, device="cpu", compute_type="int8",
                         download_root="/tmp")
    # print("finish load")
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
    lang = request.args.get("lang", None)

    # data = file.read()
    # print("start transcribe")
    segments, info = model.transcribe(
        file, beam_size=5, language=lang, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))
    res = []
    result = {
        "lang": info.language,
        "lang_prob": info.language_probability,
        "duration": info.duration,
        "vad_duration": info.duration_after_vad,
        "sentences": [],
    }
    for segment in segments:
        result["sentences"].append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
        })

        # res.append("[%.2fs -> %.2fs] %s" %
        #            (segment.start, segment.end, segment.text))

        # rest = "Detected language '%s' with probability %f" % (
        #     info.language, info.language_probability)

    return jsonify(result)


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
    tree = {}
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        # indent = ' ' * 4 * (level)
        # tree.append(
        #     '{}'.format(os.path.basename(root))
        # )
        tree[
            os.path.basename(root)
        ] = []
        data = []
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            data.append(
                f
            )
        for d in dirs:
            inside = list_files(
                os.path.join(startpath, d)
            )
            for i in inside:
                data.append(
                    i
                )
        tree[os.path.basename(root)] = data
    return tree


@app.route("/lookup")
def lookup():
    tree = list_files("/app")
    return jsonify(tree)


@app.route("/dirlookup")
def dirlookup():
    dir_ = request.args.get('dir')
    if not dir_:
        return None
    tree = list_files(dir_)
    return jsonify(tree)


if __name__ == '__main__':
    app.run(debug=True, port=8000)

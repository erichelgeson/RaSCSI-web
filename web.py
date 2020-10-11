import os

from flask import Flask, render_template, request, flash, url_for, redirect
from werkzeug.utils import secure_filename

from ractl_cmds import attach_image, list_devices, is_active, list_files, detach_by_id, reboot_pi, shutdown_pi, \
    download_file_to_iso, base_dir

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           devices=list_devices(),
                           active=is_active(),
                           files=list_files())


@app.route('/scsi/attach', methods=['POST'])
def attach():
    file_name = request.form.get('file_name')
    scsi_id = request.form.get('scsi_id')

    # Validate image type by suffix
    if file_name.lower().endswith('.iso') or file_name.lower().endswith('iso'):
        image_type = "cd"
    elif file_name.lower().endswith('.hda'):
        image_type = "hd"
    else:
        flash(u'Unknown file type. Valid files are .iso, .hda, .cdr', 'error')
        return redirect(url_for('index'))

    process = attach_image(scsi_id, file_name, image_type)
    if process.returncode == 0:
        flash('Attached '+ file_name + " to scsi id " + scsi_id + "!")
        return redirect(url_for('index'))
    else:
        flash(u'Failed to attach '+ file_name + " to scsi id " + scsi_id + "!", 'error')
        print(process.stdout.decode("utf-8"))
        print(process.stderr.decode("utf-8"))
        flash(process.stdout.decode("utf-8"), 'stdout')
        flash(process.stderr.decode("utf-8"), 'stderr')
        return redirect(url_for('index'))


@app.route('/scsi/detach', methods=['POST'])
def detach():
    scsi_id = request.form.get('scsi_id')
    process = detach_by_id(scsi_id)
    if process.returncode == 0:
        flash("Detached scsi id " + scsi_id + "!")
        return redirect(url_for('index'))
    else:
        flash(u"Failed to detach scsi id " + scsi_id + "!", 'error')
        flash(process.stdout, 'stdout')
        flash(process.stderr, 'stderr')
        return redirect(url_for('index'))


@app.route('/pi/restart', methods=['POST'])
def restart():
    reboot_pi()
    flash("Restarting...")
    return redirect(url_for('index'))


@app.route('/pi/shutdown', methods=['POST'])
def shutdown():
    shutdown_pi()
    flash("Shutting down...")
    return redirect(url_for('index'))


@app.route('/files/download', methods=['POST'])
def download_file():
    scsi_id = request.form.get('scsi_id')
    url = request.form.get('url')
    process = download_file_to_iso(scsi_id, url)
    if process.returncode == 0:
        flash("File Downloaded")
        return redirect(url_for('index'))
    else:
        flash(u"Failed to download file", 'error')
        flash(process.stdout, 'stdout')
        flash(process.stderr, 'stderr')
        return redirect(url_for('index'))


@app.route('/files/upload', methods=['POST'])
def upload_file():
    print("upload file")
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index', filename=filename))


if __name__ == "__main__":
    app.secret_key = 'rascsi_is_awesome_insecure_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = base_dir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 # 1gb

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
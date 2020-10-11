from flask import Flask, render_template, request, flash, url_for, redirect

from ractl_cmds import attach_image, list_devices, is_active, list_files, detach_by_id

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


if __name__ == "__main__":
    app.secret_key = 'rascsi_is_awesome_insecure_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
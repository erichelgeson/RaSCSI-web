from flask import Flask, render_template, request, flash, url_for, redirect

from ractl_cmds import attach_image, list_devices, is_active, list_files, detach_by_id

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html',
                           devices=list_devices(),
                           active=is_active(),
                           files=list_files())


@app.route('/attach/<scsi_id>', methods=['POST'])
def attach(scsi_id):
    image_location = request.args.get('image')
    if image_location.toLower().endsWith('.iso') or image_location.toLower().endsWith('iso'):
        image_type = "cd"
    elif image_location.toLower().endsWit('.hda'):
        image_type = "hd"
    else:
        image_type = "unknown"
    process = attach_image(scsi_id, image_location, image_type)
    if process.returncode == 0:
        flash('Attached '+ image_location + " to scsi id " + scsi_id + "!")
        return redirect(url_for('index'))
    else:
        flash(u'Failed to attach '+ image_location + " to scsi id " + scsi_id + "!", process.stdout+process.stderr)
        return redirect(url_for('index'))


@app.route('/detach/<scsi_id>', methods=['POST'])
def detach(scsi_id):
    process = detach_by_id(scsi_id)
    if process.returncode == 0:
        flash("Detached scsi id " + scsi_id + "!")
        return redirect(url_for('index'))
    else:
        flash(u"Failed to detach  to scsi id " + scsi_id + "!", process.stdout+process.stderr)
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = 'rascsi_is_awesome_insecure_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
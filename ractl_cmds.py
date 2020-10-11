import fnmatch
import os
import subprocess
import time
import re

base_dir = "/home/pi/images"  # Default
valid_file_types = ['*.hda', '*.iso', '*.cdr']
valid_file_types = r'|'.join([fnmatch.translate(x) for x in valid_file_types])


def is_active():
    process = subprocess.run(["systemctl", "is-active", "rascsi"], capture_output=True)
    return process.stdout.decode("utf-8").strip() == "active"


def list_files():

    files_list = []
    for path, dirs, files in os.walk(base_dir):
        # Only list valid file types
        files = [f for f in files if re.match(valid_file_types, f)]
        files_list.extend([
            (os.path.join(path, file),
             # TODO: move formatting to template
             '{:,.0f}'.format(os.path.getsize(os.path.join(path, file)) / float(1 << 20)) + " MB")
            for file in files])
    return files_list


def attach_image(scsi_id, image, type):
    return subprocess.run(["rasctl", "-c", "attach", "-t", type, "-i", scsi_id, "-f", image], capture_output=True)


def detach_by_id(scsi_id):
    return subprocess.run(["rasctl", "-c" "detach", "-i", scsi_id], capture_output=True)


def disconnect_by_id(scsi_id):
    return subprocess.run(["rasctl", "-c", "disconnect", "-i", scsi_id], capture_output=True)


def eject_by_id(scsi_id):
    return subprocess.run(["rasctl", "-i", scsi_id, "-c", "eject"])


def insert(scsi_id, file_name):
    return subprocess.run(["rasctl", "-i", scsi_id, "-c", "insert", "-f", base_dir + file_name], capture_output=True)


def create_new_image(file_name, size):
    return subprocess.run(["dd", "if=/dev/zero", "of=" + base_dir + file_name, "bs=1M", "count=" + size],
                          capture_output=True)


def delete_image(file_name):
    full_path = base_dir + "/" + file_name
    if os.path.exists(full_path):
        os.remove(base_dir + "/" + file_name)
        return True
    else:
        return False


def rascsi_service(action):
    # start/stop/restart
    return subprocess.run(["sudo", "/bin/systemctl", action, "rascsi.service"]).returncode == 0


def reboot_pi():
    return subprocess.run(["sudo", "reboot"]).returncode == 0


def shutdown_pi():
    return subprocess.run(["sudo", "shutdown", "-h", "now"]).returncode == 0


def list_devices():
    device_list = []
    output = subprocess.run(["rasctl", "-l"], capture_output=True).stdout.decode("utf-8")
    for line in output.splitlines():
        # Valid line to process, continue
        if not line.startswith("+") and \
                not line.startswith("| ID |") and \
                (not line.startswith("No device is installed.") or line.startswith("No images currently attached.")) \
                and len(line) > 0:
            line.rstrip()
            device = {}
            segments = line.split("|")
            device['id'] = segments[1].strip()
            device['un'] = segments[2].strip()
            device['type'] = segments[3].strip()
            device['file'] = segments[4].strip()
            device_list.append(device)
    return device_list


def new_file_available_name():
    return "new_file." + str(int(time.time())) + ".hda"


def download_file_to_iso(scsi_id, url):
    import urllib.request
    file_name = url.split('/')[-1]
    tmp_ts = int(time.time())
    tmp_dir = "/tmp/" + str(tmp_ts)
    os.mkdir(tmp_dir)
    tmp_full_path = tmp_dir + "/" + file_name
    iso_filename = base_dir + "/" + file_name + ".iso"

    urllib.request.urlretrieve(url, tmp_full_path)
    iso_proc = subprocess.run(["genisoimage", "-hfs", "-o", iso_filename, tmp_full_path], capture_output=True)
    if iso_proc.returncode != 0:
        return iso_proc
    return attach_image(scsi_id, iso_filename, "cd")

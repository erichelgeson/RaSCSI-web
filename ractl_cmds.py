import os
import subprocess
from os import listdir
from os.path import isfile, join, getsize
from time import gmtime

base_dir = "/home/pi/images"  # Default


def is_active():
    return subprocess.run(["systemctl", "is-active", "rascsi"], capture_output=True).stdout.strip() == "Running"


def list_files():
    files_list = []
    for path, dirs, files in os.walk(base_dir):
        files_list.extend([
            (os.path.join(path, file),
             # TODO: move formatting to template
             '{:,.0f}'.format(os.path.getsize(os.path.join(path, file)) / float(1 << 20)) + " MB")
            for file in files])
    return files_list


def attach_image(image, scsi_id, type):
    # Let RaSCSI try to figure out the type
    if type == "unknown":
        return subprocess.run(["rasctl", "-c", "attach", "-i", scsi_id, image], capture_output=True)
    else:
        return subprocess.run(["rasctl", "-c", "attach", "-t", type, "-i", scsi_id, image], capture_output=True)


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
        if not line.startswith("+") and not line.startswith("| ID |") and len(line) > 0:
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
    return "new_file." + str(gmtime()) + ".hda"
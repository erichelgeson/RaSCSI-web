import subprocess


def rascsi_service(action):
    # start/stop/restart
    return subprocess.run(["sudo", "/bin/systemctl", action, "rascsi.service"]).returncode == 0


def reboot_pi():
    return subprocess.run(["sudo", "reboot"]).returncode == 0


def shutdown_pi():
    return subprocess.run(["sudo", "shutdown", "-h", "now"]).returncode == 0
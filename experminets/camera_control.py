import requests

# Camera IP address
CAMERA_IP = '192.168.116.111'

# Base URL for camera control
BASE_URL = f'http://{CAMERA_IP}/cgi-bin/ptzctrl.cgi?ptzcmd&'

def send_command(command):
    url = BASE_URL + command
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Command '{command}' sent successfully.")
    else:
        print(f"Failed to send command '{command}'. Status code: {response.status_code}")

# Example commands
pan_command = 'left&120&10'  # Pan left with speed 12 and tilt speed 10
tilt_command = 'up&10&10'   # Tilt up with speed 10 and pan speed 10
zoom_command = 'zoomin&5'   # Zoom in with speed 5
focus_command = 'focusin&3' # Focus in with speed 3

# Send commands
send_command(pan_command)
send_command(tilt_command)
send_command(zoom_command)
send_command(focus_command)

# Stop all movements
send_command('ptzstop')
send_command('zoomstop')
send_command('focusstop')
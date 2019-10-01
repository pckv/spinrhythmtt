import argparse
import json
import socket

import mouse
import screeninfo


knob_max = 0x8000


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Host a webserver for Android Spin Rhythm controller. Source: https://github.com/pckv/spinrhythmtt')
    parser.add_argument('--host', default='0.0.0.0', help='The outgoing IP address. Leave default to open for all networks (0.0.0.0)')
    parser.add_argument('-p', '--port', default=14854, type=int, help='The webserver port. Default port is 14854')
    parser.add_argument('-m', '--monitor', default=0, type=int, help='Index of the monitor you want to use for mouse movement, starting at 0')
    parser.add_argument('-s', '--sensitivity', default=0.5, type=float, help='Sensitivity of the knobs as a floating point number. A sensitivity of 1 means the cursor will wrap around the screen after 1 full rotation. Default sensitivity is 0.5')
    args = parser.parse_args()

    monitor = list(screeninfo.get_monitors())[args.monitor]
    conversion = monitor.width / knob_max
    print('running on monitor ', args.monitor, ': ', monitor, sep='')
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    
    pressed = False
    prev_left = 0
    
    # Continuously read data from the socket
    print('Server setup, connect to ', socket.gethostbyname(socket.gethostname()), ':', args.port, sep='')
    while True:
        data, addr = sock.recvfrom(1024)
        left, button = json.loads(data.decode())
        
        x, y = mouse.get_position()
        x -= monitor.x
        
        # Move the mouse
        if left != prev_left:
            # Correction for axis when knob is turned past a full rotation
            if left > (knob_max - knob_max / 8) and prev_left < knob_max / 8:
                prev_left += knob_max
            elif left < knob_max / 8 and prev_left > (knob_max - knob_max / 8):
                prev_left -= knob_max

            mouse.move((x + int((left - prev_left) * conversion * args.sensitivity)) % monitor.width + monitor.x, y)
            prev_left = left
        
        # Handle mouse press
        if button and not pressed:
            pressed = True
            mouse.press()
        elif not button and pressed:
            pressed = False
            mouse.release()


if __name__ == '__main__':
    main()
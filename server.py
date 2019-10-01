import argparse
import json
import socket


# The maximum value of a knob from the joystick, 2^15
KNOB_MAX = 0x8000

# A global sensitivity for relative movement of a vJoy axis
JOYSTICK_SENSITIVITY = 20


def create_mouse_handler(args):
    import mouse, screeninfo
    
    monitor = list(screeninfo.get_monitors())[args.monitor]
    conversion = monitor.width / KNOB_MAX
    print('moving mouse on monitor ', args.monitor, ': ', monitor, sep='')
    
    def update_mouse(value, button, prev_value, prev_button):
        x, y = mouse.get_position()
        x -= monitor.x
        
        # Move the mouse
        if value != prev_value:
            mouse.move((x + int((value - prev_value) * conversion * args.sensitivity)) % monitor.width + monitor.x, y)
        
        # Handle mouse press
        if button and not prev_button:
            mouse.press()
        elif not button and prev_button:
            mouse.release()
    
    return update_mouse

    
def create_vjoy_handler(args):
    import pyvjoy
    
    device = pyvjoy.VJoyDevice(args.device)
    print('using vJoy device', device)
    
    def update_vjoy(value, button, prev_value, prev_button):
        device.set_axis(pyvjoy.HID_USAGE_X, int(KNOB_MAX / 2 + (value - prev_value) * args.sensitivity * JOYSTICK_SENSITIVITY))
        device.set_button(1, button)
    
    return update_vjoy


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Host a webserver for Android Spin Rhythm controller. Source: https://github.com/pckv/spinrhythmtt')
    parser.add_argument('--host', default='0.0.0.0', help='The outgoing IP address. Leave default to open for all networks (0.0.0.0)')
    parser.add_argument('-p', '--port', default=14854, type=int, help='The webserver port. Default port is 14854')
    parser.add_argument('-s', '--sensitivity', default=1, type=float, help='Sensitivity of the knobs as a floating point number.')
    parser.add_argument('-d', '--device', default=1, help='The vJoy device to use. Default device is 1')
    
    parser.add_argument('--mouse', action='store_true', help='Move the mouse instead of a vJoy device. This method only works without raw input enabled')
    parser.add_argument('-m', '--monitor', default=0, type=int, help='Index of the monitor you want to use for mouse movement, starting at 0')
    
    args = parser.parse_args()
    
    if args.mouse:
        handler = create_mouse_handler(args)
    else:
        handler = create_vjoy_handler(args)
    
    prev_value = prev_button = 0
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    
    # Continuously read data from the socket
    print('Server setup, connect to ', socket.gethostbyname(socket.gethostname()), ':', args.port, sep='')
    while True:
        data, addr = sock.recvfrom(1024)
        value, button = json.loads(data.decode())
        
        # Correction for axis when knob is turned past a full rotation
        if value != prev_value:
            if value > (KNOB_MAX - KNOB_MAX / 8) and prev_value < KNOB_MAX / 8:
                prev_value += KNOB_MAX
            elif value < KNOB_MAX / 8 and prev_value > (KNOB_MAX - KNOB_MAX / 8):
                prev_value -= KNOB_MAX
        
        handler(value, button, prev_value, prev_button)
        prev_value, prev_button = value, button


if __name__ == '__main__':
    main()
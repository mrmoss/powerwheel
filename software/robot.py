#!/usr/bin/env python3
'''
Robot side runner
'''
import sys
import time
import pygame
import serial

import shared
import robot_lib

def handle_payload_motors(ser, payload):
    '''
    Converts payload motor data into serial packets
    '''
    if not payload or 'motors' not in payload:
        return None

    if payload['mode'] != 'manual':
        print(payload)

    left = payload.get('motors', {}).get('left', 0)
    right = payload.get('motors', {}).get('right', 0)

    dir_left = int(left < 0)
    dir_right = int(right < 0)
    pwm_left = int(abs(left))
    pwm_right = int(abs(right))

    crc = dir_left ^ pwm_left ^ dir_right ^ pwm_right
    data_bytes = [0xf0, 0x0f, dir_left, pwm_left, dir_right, pwm_right, crc]
    ser.write(data_bytes)

    return True

def handle_serial_data(ser):
    '''
    Read all data from serial port and print it out
    '''
    while True:
        try:
            in_data = ser.read(1024)
        except serial.SerialException:
            break

        if not in_data:
            break

        try:
            print(in_data.decode('utf8'), end='', flush=True)
        except UnicodeDecodeError:
            pass


def main():
    '''
    Program start
    '''
    # Constants
    timeout = 0.01
    variables = { 'remote_timer': 0, 'remote_timeout_secs': 1 }

    # Driver comms
    sock = robot_lib.create_rx_socket()

    while True:
        try:
            # Open serial
            with serial.Serial(sys.argv[1], 115200, timeout=timeout) as ser:

                # Give robot a few seconds to wake up
                time.sleep(2)

                # Init pygame
                pygame.init()
                display = pygame.display.set_mode((300, 300))

                # Init joystick
                pygame.joystick.init()
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                joystick_deadzone = 0.1

                # Input states used for tracking keyboard events
                input_states = { 'joy': {} }

                # Program loop
                while True:
                    # Get pygame events
                    for event in pygame.event.get():
                        # Gui close events == quit
                        if event.type == pygame.QUIT:
                            shared.quit()

                        # Key pressed
                        if event.type == pygame.KEYDOWN:
                            input_states[event.key] = True
                            continue

                        # Key released
                        if event.type == pygame.KEYUP:
                            input_states[event.key] = False
                            continue

                        # Joystick axis moved
                        if event.type == pygame.JOYAXISMOTION:
                            val = event.value
                            if (val < 0 and val > -joystick_deadzone) or (val > 0 and val < joystick_deadzone):
                                val = 0
                            input_states['joy'][event.axis] = val

                    # Main loop
                    loop(sock, ser, display, input_states, variables)

                    # Give CPU a break
                    time.sleep(timeout)
        except serial.serialutil.SerialException:
            print('Restarting')
            time.sleep(2)

def loop(sock, ser, display, input_states, variables):
    '''
    Program loop
    '''
    # Quit
    if input_states.get(pygame.K_ESCAPE, False):
        shared.quit()

    # Print any serial data
    handle_serial_data(ser)

    # Remote control
    while robot_lib.sock_has_data(sock):
        payload = robot_lib.sock_recv_auth(sock, 'imaprettykitty', 1)
        handle_payload_motors(ser, payload)
        variables['remote_timer'] = time.time() + variables['remote_timeout_secs']
    if time.time() < variables['remote_timer']:
        return

    # Local control
    speed = 255
    if input_states.get(pygame.K_DOWN, False):
        handle_payload_motors(ser, { 'mode': 'manual', 'motors': { 'left': -speed, 'right': -speed }})
        return
    if input_states.get(pygame.K_UP, False):
        handle_payload_motors(ser, { 'mode': 'manual', 'motors': { 'left': speed, 'right': speed }})
        return
    if input_states.get(pygame.K_RIGHT, False):
        handle_payload_motors(ser, { 'mode': 'manual', 'motors': { 'left': speed, 'right': -speed }})
        return
    if input_states.get(pygame.K_LEFT, False):
        handle_payload_motors(ser, { 'mode': 'manual', 'motors': { 'left': -speed, 'right': speed }})
        return

    if input_states['joy']:
        axis_x = input_states['joy'].get(2, 0)
        axis_y = -input_states['joy'].get(3, 0)
        left = shared.clamp((axis_y - axis_x) * speed, -speed, speed)
        right = shared.clamp((axis_y + axis_x) * speed, -speed, speed)
        handle_payload_motors(ser, { 'mode': 'manual', 'motors': {'left': left, 'right': right }})
        return

    handle_payload_motors(ser, { 'mode': 'manual', 'motors': { 'left': 0, 'right': 0 }})


if __name__ == '__main__':
    main()

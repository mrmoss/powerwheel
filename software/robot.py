#!/usr/bin/env python3
'''
Robot side runner
'''
import struct
import sys
import time
import pygame
import serial

import shared
import robot_lib

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


def handle_payload_motors(ser, payload):
    '''
    Converts payload motor data into serial packets
    '''
    if not payload or 'motors' not in payload:
        return None

    left = int(payload.get('motors', {}).get('left', 0))
    right = int(payload.get('motors', {}).get('right', 0))

    crc = left ^ right
    ser.write(struct.pack('>BBbbb', 0xf0, 0x0f, left, right, crc))

    return True

def loop(display, input_states, args):
    '''
    Program loop
    '''
    sock, ser, variables = args

    # Print any serial data
    handle_serial_data(ser)

    # Remote control
    while robot_lib.sock_has_data(sock):
        handle_payload_motors(ser, robot_lib.sock_recv_auth(sock, 'imaprettykitty', 1))
        variables['remote_timer'] = time.time() + variables['remote_timeout_secs']
    if time.time() < variables['remote_timer']:
        return

    # Local control
    speed = 127
    if input_states.get(pygame.K_UP, False):
        handle_payload_motors(ser, { 'controller': 'robot', 'motors': { 'left': speed, 'right': speed }})
        return
    if input_states.get(pygame.K_RIGHT, False):
        handle_payload_motors(ser, { 'controller': 'robot', 'motors': { 'left': speed, 'right': -speed }})
        return
    if input_states.get(pygame.K_DOWN, False):
        handle_payload_motors(ser, { 'controller': 'robot', 'motors': { 'left': -speed, 'right': -speed }})
        return
    if input_states.get(pygame.K_LEFT, False):
        handle_payload_motors(ser, { 'controller': 'robot', 'motors': { 'left': -speed, 'right': speed }})
        return

    if input_states['joy']:
        axis_x = input_states['joy'].get(2, 0)
        axis_y = -input_states['joy'].get(3, 0)
        left = shared.clamp((axis_y - axis_x) * speed, -speed, speed)
        right = shared.clamp((axis_y + axis_x) * speed, -speed, speed)
        handle_payload_motors(ser, { 'mode': 'robot', 'motors': {'left': left, 'right': right }})
        return

    handle_payload_motors(ser, { 'mode': 'robot', 'motors': { 'left': 0, 'right': 0 }})


def main():
    '''
    Program start
    '''
    # Constants
    variables = { 'remote_timer': 0, 'remote_timeout_secs': 1 }

    # Driver comms
    sock = robot_lib.create_rx_socket()

    # Open serial
    while True:
        try:
            with serial.Serial(sys.argv[1], 115200, timeout=0.01) as ser:
                # Give robot a few seconds to wake up
                time.sleep(2)

                # Start program loop
                shared.loop(loop, 'robot', (sock, ser, variables))

        except serial.serialutil.SerialException:
            print('Restarting')
            time.sleep(2)


if __name__ == '__main__':
    main()

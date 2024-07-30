#!/usr/bin/env python3
import sys
import time
import pygame
import serial

import robot_lib

def write_serial(ser, dir_left, pwm_left, dir_right, pwm_right):
    crc = dir_left ^ pwm_left ^ dir_right ^ pwm_right
    data_bytes = [0xf0, 0x0f, dir_left, pwm_left, dir_right, pwm_right, crc]
    ser.write(data_bytes)

def print_serial(ser):
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
    sock = robot_lib.create_rx_socket()

    with serial.Serial(sys.argv[1], 115200, timeout=0.1) as ser:
        ser.flush()
        time.sleep(2)

        pygame.init()
        _display = pygame.display.set_mode((300, 300))

        key_states = {}

        while True:
            time.sleep(0.0001)
            print_serial(ser)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    key_states[event.key] = True
                    continue
                if event.type == pygame.KEYUP:
                    key_states[event.key] = False
                    continue

            # Remote control
            payload = None
            while robot_lib.sock_has_data(sock):
                payload = robot_lib.sock_recv_auth(sock, 'imaprettykitty', 5)
            if payload:
                write_serial(
                    ser,
                    payload.get('dir_left', 0),
                    payload.get('pwm_left', 0),
                    payload.get('dir_right', 0),
                    payload.get('pwm_right', 0)
                )
                continue

            # Local control
            speed = 100
            if key_states.get(pygame.K_DOWN, False):
                print('1')
                write_serial(ser, 1, speed, 1, speed)
            elif key_states.get(pygame.K_UP, False):
                print('2')
                write_serial(ser, 0, speed, 0, speed)
            elif key_states.get(pygame.K_RIGHT, False):
                print('3')
                write_serial(ser, 1, speed, 0, speed)
            elif key_states.get(pygame.K_LEFT, False):
                print('4')
                write_serial(ser, 0, speed, 1, speed)
            else:
                write_serial(ser, 0, 0, 0, 0)

if __name__ == '__main__':
    main()

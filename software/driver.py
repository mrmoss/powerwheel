#!/usr/bin/env python3
'''
Driver side runner
'''
import time
import pygame

import shared
import robot_lib

def handle_payload_motors(sock, payload):
    robot_lib.sock_send_auth(sock, 'imaprettykitty', payload)

def loop(display, input_states, sock):
    '''
    Program loop
    '''
    # Arrow keys
    speed = 127
    if input_states.get(pygame.K_UP, False):
        handle_payload_motors(sock, { 'controller': 'driver', 'motors': { 'left': speed, 'right': speed }})
        return
    if input_states.get(pygame.K_RIGHT, False):
        handle_payload_motors(sock, { 'controller': 'driver', 'motors': { 'left': speed, 'right': -speed }})
        return
    if input_states.get(pygame.K_DOWN, False):
        handle_payload_motors(sock, { 'controller': 'driver', 'motors': { 'left': -speed, 'right': -speed }})
        return
    if input_states.get(pygame.K_LEFT, False):
        handle_payload_motors(sock, { 'controller': 'driver', 'motors': { 'left': -speed, 'right': speed }})
        return

    tank = False

    if input_states['joy']:
        left = 0
        right = 0
        if tank:
            axis_x = -input_states['joy'].get(2, 0)
            axis_y = -input_states['joy'].get(3, 0)
            left = shared.clamp((axis_y + axis_x) * speed, -speed, speed)
            right = shared.clamp((axis_y - axis_x) * speed, -speed, speed)
        else:
            left = -input_states['joy'].get(3, 0) * speed
            right = -input_states['joy'].get(1, 0) * speed

        left = int(shared.clamp(left, -speed, speed))
        right = int(shared.clamp(left, -speed, speed))

        handle_payload_motors(sock, { 'controller': 'driver', 'motors': { 'left': left, 'right': right }})
        return

    handle_payload_motors(sock, { 'controller': 'driver', 'motors': { 'left': 0, 'right': 0 }})

def main():
    '''
    Program start
    '''
    # Driver comms
    sock = robot_lib.create_tx_socket()

    # Start program loop
    shared.loop(loop, 'robot', sock)


if __name__ == '__main__':
    main()

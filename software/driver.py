#!/usr/bin/env python3
'''
Lidar (robot) sender side
'''
import json
import sys
import time
import pygame

import robot_lib

def loop(sock, payload, display, input_states):
    '''
    Program loop
    '''
    # Quit
    if input_states.get(pygame.K_ESCAPE, False):
        quit()

    # Drive robot
    speed = 100
    if input_states.get(pygame.K_DOWN, False):
        payload['motors'] = {'left': -speed, 'right': -speed }
        return
    if input_states.get(pygame.K_UP, False):
        payload['motors'] = {'left': speed, 'right': speed }
        return
    if input_states.get(pygame.K_RIGHT, False):
        payload['motors'] = {'left': speed, 'right': -speed }
        return
    if input_states.get(pygame.K_LEFT, False):
        payload['motors'] = {'left': -speed, 'right': speed }
        return
    payload['motors'] = {'left': 0, 'right': 0 }

def main():
    '''
    Program start
    '''
    # Constants
    timeout = 0.0001

    # Driver comms
    sock = robot_lib.create_tx_socket()

    # Init pygame
    pygame.init()
    display = pygame.display.set_mode((300, 300))

    # Input states used for tracking keyboard events
    input_states = {}

    # Stateful payload object
    payload = {}

    # Program loop
    while True:
        # Get pygame events
        for event in pygame.event.get():
            # Gui close events == quit
            if event.type == pygame.QUIT:
                quit()

            # Key pressed
            if event.type == pygame.KEYDOWN:
                input_states[event.key] = True
                continue

            # Key released
            if event.type == pygame.KEYUP:
                input_states[event.key] = False
                continue

        # Main loop
        loop(sock, payload, display, input_states)

        # Send payload to robot
        print(payload)
        robot_lib.sock_send_auth(sock, 'imaprettykitty', payload)

        # Give CPU a break
        time.sleep(timeout)



if __name__ == '__main__':
    main()

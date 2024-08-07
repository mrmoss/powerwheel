#!/usr/bin/env python3
'''
Driver side runner
'''
import time
import pygame

import shared
import robot_lib

def loop(sock, payload, display, input_states):
    '''
    Program loop
    '''
    # Quit
    if input_states.get(pygame.K_ESCAPE, False):
        shared.quit()

    # Drive robot
    speed = 255
    speed2 = 120
    if input_states.get(pygame.K_DOWN, False):
        payload['motors'] = {'left': -speed, 'right': -speed2 }
        return
    if input_states.get(pygame.K_UP, False):
        payload['motors'] = {'left': speed, 'right': speed2 }
        return
    if input_states.get(pygame.K_RIGHT, False):
        payload['motors'] = {'left': -speed, 'right': speed }
        return
    if input_states.get(pygame.K_LEFT, False):
        payload['motors'] = {'left': speed, 'right': -speed }
        return

    if input_states['joy']:
        axis_x = input_states['joy'].get(2, 0)
        axis_y = -input_states['joy'].get(3, 0)
        left = shared.clamp((axis_y + axis_x) * speed, -speed, speed)
        right = shared.clamp((axis_y - axis_x) * speed, -speed, speed)
        payload['motors'] = {'left': left, 'right': right }
        return

    payload['motors'] = {'left': 0, 'right': 0 }

def main():
    '''
    Program start
    '''
    # Constants
    timeout = 0.01

    # Driver comms
    sock = robot_lib.create_tx_socket()

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

    # Stateful payload object
    payload = { 'mode': 'remote'}

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
        loop(sock, payload, display, input_states)

        # Send payload to robot
        print(payload)
        robot_lib.sock_send_auth(sock, 'imaprettykitty', payload)

        # Give CPU a break
        time.sleep(timeout)


if __name__ == '__main__':
    main()

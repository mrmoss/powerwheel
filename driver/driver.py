#!/usr/bin/env python3
'''
Lidar (robot) sender side
'''
import json
import sys
import time
import pygame

import robot_lib

def main():
    '''
    Main
    '''
    sock = robot_lib.create_tx_socket()

    pygame.init()
    _display = pygame.display.set_mode((300, 300))

    key_states = {}

    while True:
        time.sleep(0.01)

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

        speed = 100
        payload = { 'dir_left': 0, 'pwm_left': 0, 'dir_right': 1, 'pwm_right': 0 }
        if key_states.get(pygame.K_DOWN, False):
            print('1')
            payload = { 'dir_left': 1, 'pwm_left': speed, 'dir_right': 1, 'pwm_right': speed }
        elif key_states.get(pygame.K_UP, False):
            print('2')
            payload = { 'dir_left': 0, 'pwm_left': speed, 'dir_right': 0, 'pwm_right': speed }
        elif key_states.get(pygame.K_RIGHT, False):
            print('3')
            payload = { 'dir_left': 1, 'pwm_left': speed, 'dir_right': 0, 'pwm_right': speed }
        elif key_states.get(pygame.K_LEFT, False):
            print('4')
            payload = { 'dir_left': 0, 'pwm_left': speed, 'dir_right': 1, 'pwm_right': speed }

        if payload:
            payload['nonce'] = time.time()
            robot_lib.sock_send_auth(sock, 'imaprettykitty', payload)



if __name__ == '__main__':
    main()

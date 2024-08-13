#!/usr/bin/env python3
'''
Shared functions
'''
import sys
import time
import pygame

def joystick_init():
    '''
    Initializes joystick
    '''
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        print('JOYSTICK FOUND')
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return joystick

    return None

def joystick_handle_axis_event(event):
    joystick_deadzone = 0.1
    val = event.value
    if (val < 0 and val > -joystick_deadzone) or (val > 0 and val < joystick_deadzone):
        val = 0
    return val

def clamp(val, low, high):
    '''
    Returns low if val < low, high if val > high, and val otherwise
    '''
    return min(high, max(low, val))


def quit():
    '''
    Quits pygame and kills process
    '''
    pygame.quit()
    sys.exit(0)

def loop(loop_func, control_mode, args):
    # Constants
    timeout = 0.1

    # Init pygame
    pygame.init()
    display = pygame.display.set_mode((300, 300))

    # Init joystick
    joystick = joystick_init()

    # Input states used for tracking keyboard events
    input_states = { 'joy': {} }

    # Program loop
    while True:

        # Give CPU a break
        time.sleep(timeout)

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

            # Joystick axis moved
            if event.type == pygame.JOYAXISMOTION:
                input_states['joy'][event.axis] = joystick_handle_axis_event(event)
                continue

        # Escape key == quit
        if input_states.get(pygame.K_ESCAPE, False):
            quit()

        # Main loop
        loop_func(display, input_states, args)
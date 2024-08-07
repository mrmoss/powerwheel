#!/usr/bin/env python3
'''
Shared functions
'''
import sys
import pygame

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
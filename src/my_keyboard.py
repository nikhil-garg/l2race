# Driver control input from keyboard
import pygame

from src.car_command import car_command
from src.my_logger import my_logger
logger = my_logger(__name__)

def printhelp():
    print('Keyboard commands:\n'
          'drive with LEFT/UP/RIGHT/DOWN or AWDS keys\n'
          'r resets car\n'
          'ESC quits\n'
          'h|? shows this help')
class my_keyboard:

    def __init__(self):
        pygame.init()
        self.car_input = car_command()
        printhelp()

    def read(self):
        pressed = pygame.key.get_pressed()

        self.car_input.throttle = 0.
        self.car_input.brake = 0.
        self.car_input.steering = 0.
        self.car_input.reset=False

        if not any(pressed):
            return self.car_input

        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
           self.car_input.throttle=1.
           self.car_input.brake=0.
        elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
           self.car_input.throttle=0.
           self.car_input.brake=1.
        elif pressed[pygame.K_SPACE]:
            pass

        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.car_input.steering = +1. # steer in negative angle direction, i.e. CW
        elif pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            self.car_input.steering = -1. # steer in positive angle, i.e. CCW
        elif pressed[pygame.K_BACKSPACE]:
            self.car_input.reverse = not self.car_input.reverse
        elif pressed[pygame.K_ESCAPE]:
            self.car_input.quit = True
        elif pressed[pygame.K_r]:
            self.car_input.reset =True
        elif pressed[pygame.K_QUESTION] or pressed[pygame.K_h]:
            printhelp()
        else:
            self.car_input.steering = 0.
        return self.car_input

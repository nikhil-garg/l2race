"""
joystick race controller based on xbox bluetooth controller.
Xbox has 11 buttons.
buttons ABXY are first four buttons 0-3, then menu and window buttons are 4th and 5th from end, i.e. 7 and 6
"""
import logging
from typing import Tuple, Optional
import pygame # conda install -c cogsci pygame; maybe because it only is supplied for earlier python, might need conda install -c evindunn pygame ; sudo apt-get install libsdl-ttf2.0-0
from pygame import joystick
import platform
import time

INACTIVITY_RECONNECT_TIME = 5
RECONNECT_TIMEOUT = 1

from src.l2race_utils import my_logger
from src.globals import JOYSTICK_NUMBER
logger = my_logger(__name__)
# logger.setLevel(logging.DEBUG)

from src.car_command import car_command
from src.user_input import user_input

def printhelp():
    print('\n-----------------------------------\nJoystick commands:\n'
          'steer with left joystick left|right\n'
          'throttle is right paddle, brake is left paddle\n'
          'B activates reverse gear\n'
          'Y activates autordrive control (if implemented)\n'
          'Menu button (to left of XYBA buttons) resets car\n'
          'X restarts client from scratch (if server went down)\n'
          'Windows button (by left joystick) quits\n-----------------------------------\n'
          )


class my_joystick:
    """"
    The read() method gets joystick input to return (car_command, user_input)
    """
    XBOX_ONE_BLUETOOTH_JOYSTICK = 'Xbox One S Controller'
    XBOX_WIRED = 'Xbox 360 Wireless Receiver' #Although in the name the word 'Wireless' appears, the controller is wired
    XBOX_ELITE = 'Xbox One Elite Controller'

    def __init__(self, joystick_number=JOYSTICK_NUMBER):
        """
        Makes a new joystick instance.

        :param joystick_number: use if there is more than one joystick
        :returns: the instance

        :raises RuntimeWarning if no joystick is found or it is unknown type
        """
        self.joy:Optional[joystick.Joystick]=None
        self.car_command:car_command=car_command()
        self.user_input:user_input = user_input()
        self.default_car_command=car_command()
        self.default_user_input=user_input()
        self.numAxes:Optional[int]=None
        self.numButtons:Optional[int]=None
        self.axes=None
        self.buttons=None
        self.name:Optional[str]=None
        self.joystick_number:int=joystick_number
        self.lastTime = 0
        self.lastActive = 0

        self._rev_was_pressed=False # to go to reverse mode or toggle out of it
        joystick.init()
        count = joystick.get_count()
        if count<1:
            raise RuntimeWarning('no joystick(s) found')

        self.lastActive=time.time()
        if platform.system() == 'Linux':
            if self.joystick_number == 0:
                self.joy = joystick.Joystick(3) # TODO why?
            else:
                self.joy = joystick.Joystick(4 - self.joystick_number)  # TODO why is this cryptic code needed? What does it do?
        else:
            self.joy = joystick.Joystick(self.joystick_number)
        self.joy.init()
        self.numAxes = self.joy.get_numaxes()
        self.numButtons = self.joy.get_numbuttons()
        self.name=self.joy.get_name()
        if not self.name==my_joystick.XBOX_ONE_BLUETOOTH_JOYSTICK and not self.name==my_joystick.XBOX_ELITE and not self.name==my_joystick.XBOX_WIRED:
            logger.warning('Name: {}'.format(self.name))
            logger.warning('unknown joystick type {} found: add code to correctly map inputs by running my_joystick as main'.format(self.name))
            raise RuntimeWarning('unknown joystick type {} found'.format(self.name))
        logger.info('joystick named "{}" found with {} axes and {} buttons'.format(self.name, self.numAxes, self.numButtons))

    def _connect(self):
        """
        Tries to connect to joystick

        :return: None

        :raises RuntimeWarning if there is no joystick
        """


    def check_if_connected(self):
        """
        Periodically checks if joystick is still there if there has not been any input for a while.
        If we have not read any input for INACTIVITY_RECONNECT_TIME and we have not checked for RECONNECT_TIMEOUT, then quit() the joystick and reconstruct it.

        :raises RuntimeWarning if check fails
        """
        now = time.time()
        if now - self.lastActive > INACTIVITY_RECONNECT_TIME and now - self.lastTime > RECONNECT_TIMEOUT:
            self.lastTime = now
            pygame.joystick.quit()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                return
            else:
               raise RuntimeWarning('no joystick found')


    def read(self) -> Tuple[car_command,user_input]:
        """
        Returns the car_command, user_input tuple. Use check_if_connected() and connect() to check and connect to joystick.

        :returns: the car_command,user_input

        :raises RuntimeWarning if joystick disappears
        """

        self.check_if_connected()

        self.user_input.restart_client=self.joy.get_button(2) # X button
        self.car_command.reverse = True if self.joy.get_button(1) == 1 else False  # B button
        if not self.car_command.reverse: # only if not in reverse
            self.car_command.autodrive_enabled = True if self.joy.get_button(3) == 1 else False # Y button

        if self.name==my_joystick.XBOX_ONE_BLUETOOTH_JOYSTICK:
            self.car_command.steering = self.joy.get_axis(0) #self.axes[0], returns + for right push, which should make steering angle positive, i.e. CW
            self.car_command.throttle =  (1 + self.joy.get_axis(5)) / 2. # (1+self.axes[5])/2
            self.car_command.brake =  (1 + self.joy.get_axis(2)) / 2. #(1+self.axes[2])/2
            self.user_input.restart_car=self.joy.get_button(7) # menu button
            self.user_input.quit=self.joy.get_button(6) # windows button
        elif self.name==my_joystick.XBOX_ELITE: # antonio's older joystick
            self.car_command.steering = self.joy.get_axis(0) #self.axes[0], returns + for right push, which should make steering angle positive, i.e. CW
            self.car_command.throttle = self.joy.get_axis(5)
            self.car_command.brake = self.joy.get_axis(2)
            self.user_input.restart_car=self.joy.get_button(7) # menu button
            self.user_input.quit=self.joy.get_button(6) # windows button

        elif self.name==my_joystick.XBOX_WIRED:
            self.car_command.steering = self.joy.get_axis(0) #self.axes[0], returns + for right push, which should make steering angle positive, i.e. CW
            self.car_command.throttle = self.joy.get_button(7) #(1 + self.joy.get_button(7)) / 2.  # (1+self.axes[5])/2
            self.car_command.brake = self.joy.get_button(6) #(1 + self.joy.get_button(6)) / 2.  # (1+self.axes[2])/2
            self.user_input.restart_car = self.joy.get_button(9)  # menu button
            self.user_input.quit = self.joy.get_button(8)  # windows button

        logger.debug(self)
        return self.car_command, self.user_input

    def __str__(self):
        # axStr='axes: '
        # for a in self.axes:
        #     axStr=axStr+('{:5.2f} '.format(a))
        # butStr='buttons: '
        # for b in self.buttons:
        #     butStr=butStr+('1' if b else '_')
        #
        # return axStr+' '+butStr
        s="steer={:4.1f} throttle={:4.1f} brake={:4.1f}".format(self.car_command.steering, self.car_command.throttle, self.car_command.brake)
        return s


if __name__ == '__main__':
    joy=my_joystick()
    it=0
    while True:
        # joy.read()
        # print("steer={:4.1f} throttle={:4.1f} brake={:4.1f}".format(joy.steering, joy.throttle, joy.brake))
        pygame.event.get() # must call get() to handle internal queue
        joy.axes=list()
        for i in range(joy.numAxes):
            joy.axes.append(joy.joy.get_axis(i))

        joy.buttons=list()
        for i in range(joy.numButtons):
            joy.buttons.append(joy.joy.get_button(i))
        axStr='axes: '
        for i in joy.axes:
            axStr=axStr+('{:5.2f} '.format(i))
        butStr='buttons: '
        for i in joy.buttons:
            butStr=butStr+('1' if i else '_')


        print(str(it)+': '+axStr+' '+butStr)
        it+=1
        pygame.time.wait(300)



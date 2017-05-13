#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import rospy
import re
import time
 
# importing rospeex library
from rospeex_if import ROSpeexInterface
# importing HSR library
import hsrb_interface
 
 
class HSRControlDemo(object):
    """ HSR Control Demo class """
    def __init__(self):
        """ Initializer """
        self._interface = None
        self._robot = None
        self.whole_body = None
 
    def sr_response(self, message):
        """ speech recognition response callback
        @param message: recognize result (e.g. Move your head.)
        @type  message: str
        """
        # extract a body-part name from an utterance
        rospy.loginfo('result_received : %f', time.time())
        PATTERN_LIST=['Move your','move your']
        rospy.loginfo('you said: %s' % message)
        for pattern in PATTERN_LIST:
            parts = re.compile(pattern + ' (?P<part>.*)').search(message)
            if parts:
                target = parts.group('part')
                if re.search('head', target):
                    self.move_head()
                else:
                    rospy.loginfo('%s is not defined.' % target)
                break
 
    def move_head(self):
        """ move HSR head joint """
        text = u'I\'m moving my head.'
        self._interface.say(text, 'en', 'nict')
 
        try:
            self.whole_body.move_to_joint_positions({'arm_lift_joint': 0.1})
            self.whole_body.move_to_joint_positions({'head_pan_joint': -0.5, 'head_tilt_joint': 0.0})
            self.whole_body.move_to_joint_positions({'head_pan_joint': 0.5, 'head_tilt_joint': 0.0})
            self.whole_body.move_to_neutral()
        except:
            rospy.logerr('Failed to joint control.')
         
    def run(self):
        """ run ros node """
        # initialize hsr
        self._robot = hsrb_interface.Robot()
        # whole body controller
        self.whole_body = self._robot.get('whole_body')
        # initialize hsr pose
        self.whole_body.move_to_neutral()
        self.whole_body.move_to_joint_positions({'arm_lift_joint': 0.1})
 
        # initialize rospeex
        self._interface = ROSpeexInterface()
        self._interface.init()
        self._interface.register_sr_response(self.sr_response)
        #self._interface.set_spi_config(language='en', engine='google')
        self._interface.set_spi_config(language='en')
 
        rospy.spin()
 
if __name__ == '__main__':
    try:
        node = HSRControlDemo()
        node.run()
    except rospy.ROSInterruptException:
        pass


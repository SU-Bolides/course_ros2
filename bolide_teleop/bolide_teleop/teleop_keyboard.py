import threading
import click

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32
from bolide_interfaces.msg import SpeedDirection

# TODO - Test incrementation
# TODO - work on brake


class KeyboardController(Node):
    def __init__(self):
        super().__init__('teleop_node')
        self.get_logger().info("Teleop node started, Keyboard interrupt (ctrl+c will stop the node)")

        self.pub = self.create_publisher(SpeedDirection, '/cmd_vel', 10)

        #self.timer = self.create_timer(0.4, self.timer_callback) --> self.timer_callback will be called every 0.4s which means that periodic commands will be sent to the system so that we can't do the emergency_stop due to the presence of these commands 
        # init speed and direction
        self.current_speed = 0.0
        self.current_direction = 0.0
        self.key_mapping = {'\x1b[A': 'UP', '\x1b[B': 'DOWN',
                            '\x1b[C': 'RIGHT', '\x1b[D': 'LEFT', 's': 'BRAKE', 'q': 'QUIT', 'n': 'NEUTRAL'}

        key_mapping_str = '\n'.join([f'\t{key}: {value}' for key, value in self.key_mapping.items()])
        print(f"Key control mapping:\n{key_mapping_str}\n")

    #def timer_callback(self):
        #self.publish_speed_direction()

    def publish_speed_direction(self):
        print("publish curr_speed = ", self.current_speed)
        print("publish curr_direction = ", self.current_direction)
        self.pub.publish(SpeedDirection(speed=self.current_speed, direction=self.current_direction))

    def on_key_press(self, in_key):
        key = self.get_key_char(in_key)
        if key in self.key_mapping.keys():
            self.perform_action(self.key_mapping[key])
        else:
            self.get_logger().warn(f"[WARN] -- No actions for key : {key}")

    def on_key_release(self, in_key):
        key = self.get_key_char(in_key)
        if key in self.key_mapping.keys():
            self.perform_action(self.key_mapping[key], coeff=0)

    def get_key_char(self, key):
        if hasattr(key, 'char'):
            return key.char
        else:
            return key

    def perform_action(self,action, coeff=1.0):
        # mykey = click.getchar() 
        
        # This getchar() is blocking : if the user does not press a key, nothing happens
        # even the timer does not work correctly (because the main thread is blocked on 
        # the keyboard and the spin() is on another thread)
        
        # action = self.key_mapping[mykey]

        if action == '':
            coeff = 0.0
        if action == 'UP':
            if self.current_speed < 0.05 * coeff:
                self.current_speed += 0.05 * coeff
            else:
                self.current_speed = 0.05 * coeff
        elif action == 'DOWN':
            if self.current_speed > -0.05 * coeff:
                self.current_speed -= 0.05 * coeff
            else:
                self.current_speed = -0.05 * coeff
        elif action == 'LEFT':
            if self.current_direction > -1.0:
                self.current_direction += -1.0
            else:
                self.current_direction = -1.0
        elif action == 'RIGHT':
            if self.current_direction < 1.0:
                self.current_direction += 1.0
            else:
                self.current_direction = 1.0
        elif action == 'BRAKE':
            self.current_speed = 2.0 * coeff
        elif action == 'QUIT':
            exit()
        elif action == 'NEUTRAL':
            self.current_speed = 0.0
        else:
            self.get_logger().warn(f"Unknown action: {action}")
        self.publish_speed_direction()


def main(args=None):
    rclpy.init(args=args)
    controller = KeyboardController()
    thread = threading.Thread(target=rclpy.spin, args=(controller, ), daemon=True)
    thread.start()

    try:
        while True:
            key=click.getchar()
            controller.on_key_press(key)#perform_action()
    except KeyboardInterrupt:
        controller.get_logger().info("Shutting down teleop")
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
	main()

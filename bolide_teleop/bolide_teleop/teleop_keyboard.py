import threading
import click

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32
from bolide_interfaces.msg import SpeedDirection

# TODO - work on brake


class KeyboardController(Node):
    """ROS2 Class of the Keyboard control
    """
    def __init__(self):
        super().__init__('teleop_node')

        # PARAMS
        self.declare_parameter('debug', False)

        self.get_logger().info("[INFO] -- Teleop node started, Keyboard interrupt (CTRL+C) will stop the node")

        # A debug bool to print or not the data
        self.debug = self.get_parameter('debug').get_parameter_value().bool_value
        if self.debug:
            rclpy.logging.set_logger_level('teleop_node', 10)  # 10 is for DEBUG level

        # create publish of speed and direction
        self.speed_pub = self.create_publisher(Float32, '/cmd_vel', 10)
        self.direction_pub = self.create_publisher(Float32, '/cmd_dir', 10)

        # Timer for the data
        self.timer = self.create_timer(0.1, self.timer_callback)

        # init speed and direction
        self.current_speed = 0.0
        self.current_direction = 0.0
        self.key_mapping = {
            '\x1b[A': 'UP',     
            '\x1b[B': 'DOWN',
            '\x1b[C': 'RIGHT',
            '\x1b[D': 'LEFT', 
            's': 'BRAKE', 
            'q': 'QUIT', 
            'n': 'NEUTRAL'
        }

        key_mapping_str = '\n'.join([f'\t{key}: {value}' for key, value in self.key_mapping.items()])
        self.get_logger().info(f"[INFO] -- Key control mapping:\n{key_mapping_str}\n")

    def timer_callback(self):
        """Callback function of the timer to publish data to speed and direction topics
        """
        if self.debug:
            self.get_logger().debug(f"[DEBUG] -- current speed = {self.current_speed}")
            self.get_logger().debug(f"[DEBUG] -- current direction = {self.current_direction}")
        self.speed_pub.publish(Float32(data=self.current_speed))
        self.direction_pub.publish(Float32(data=self.current_direction))

    def perform_action(self, coeff=1.0):
        """Perform action depending on the key pressed.\
            Can be better but we want it to be simple because it is a autonomous car normally.

        Args:
            coeff (float, optional): a simple coefficient. Defaults to 1.0.
        """
        mykey = click.getchar()

        action = self.key_mapping[mykey]

        if action == '':
            coeff = 0.0
        if action == 'UP':
            self.current_speed = 0.056 * coeff
        elif action == 'DOWN':
            self.current_speed -= 0.05 * coeff
        elif action == 'LEFT':
            if self.current_direction > -1.0:
                self.current_direction -= 1.0
            else:
                self.current_direction = -1.0
        elif action == 'RIGHT':
            if self.current_direction < 1.0:
                self.current_direction += 1.0
            else:
                self.current_direction = 1.0
        elif action == 'BRAKE':
            self.current_speed = 2.0
        elif action == 'QUIT':
            exit()
        elif action == 'NEUTRAL':
            self.current_speed = 0.0
        else:
            self.get_logger().warn(f"Unknown action: {action}")


def main(args=None):
    rclpy.init(args=args)
    controller = KeyboardController()
    thread = threading.Thread(target=rclpy.spin, args=(controller, ), daemon=True)
    thread.start()

    while True:
        controller.perform_action()
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

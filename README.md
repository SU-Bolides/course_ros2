# course_ros2
The official Sorbonne University ROS2 repository for the CoVaPsy course at ENS Paris-Saclay

## Low level nodes
This repository contains only the low level code for the car and a simple teleop package.

### Bolide Interfaces
The [package](./bolide_interfaces/) containing all Messages and Services created for the car.

### Bolide Direction
The direction of the car is controlled by a Dynamixel plug with a U2D2 connector to the Raspberry Pi. The package [bolide_direction](./bolide_direction/) have a node subscribed to a SpeedDirection message, and send to the dynamixel the angle value needed. The angle is limited by the turning mechanism of the car, so we set a maximum steering angle of 15.5 degrees. To facilitate the process, the direction value of the SpeedDirection message is include in [-1, 1].
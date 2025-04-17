# course_ros2
The official Sorbonne University ROS2 repository for the CoVaPsy course at ENS Paris-Saclay

- [course\_ros2](#course_ros2)
    - [General informations](#general-informations)
  - [Launching the car (for now)](#launching-the-car-for-now)
  - [Low level nodes](#low-level-nodes)
    - [Bolide Interfaces](#bolide-interfaces)
    - [Bolide Direction](#bolide-direction)
    - [Bolide STM32](#bolide-stm32)
    - [Bolide Teleop](#bolide-teleop)
    - [Sllidar](#sllidar)


### General informations
- Raspberry Pi 5 (RPi5) - OS : Ubuntu 24.04
- ROS2 Jazzy
- Repository for Hig-Level nodes : **TODO**
- [Official repository of the race (for schematics)](https://github.com/ajuton-ens/CourseVoituresAutonomesSaclay.git)
- [Repository of last year (2024)](https://github.com/SU-Bolides/course_2025_slam_pkgs.git) : There is the main branch in ROS and the ROS2 branch

**Check the [tutorials](Tutorials.md) if you need some extra infos.**

Be prepared every time you start the car. Avoid plugging the battery if you don't want to test something with all sensors and motors, batteries take time to be charged up. You can work on the RPi5 alone or even work on your personal computer (or VM if you want absolutely to try with a ROS distro) thanks to GitHub.

Please, talking of GitHub, use it correctly ! Commit every change to keep a track of your work and easily go back if needed. By working with GitHub you can easily set up a new RPi if needed.

**You are a group so work together**, be sure that everyone are following your plan and not doing everything that they want. You will normally have two cars, it means that you can divide your group in two little groups and work on something different to be faster. The race comes really fast so at the beginning you need to fix what you want for it.

## Launching the car (for now)
**Never forget to build on your workspace folder and not your src folder !**
When the car is on, connect with ssh (you have to know its ip address before), or branch it to a display. Normally we add some lines in the .bashrc file so when you open a terminal it will be automatically on the workspace folder and all sourced up. If you need to source after a colcon build just type :
```shell
srcw
```
And to open the virtual environment just type :
```shell
vir
```

On the terminal check the connection of all USB devices (Lidar and Dynamixel) with :
```shell
ls /dev/tty*
```
if you see /dev/ttyU2D2 and /dev/ttyLIDAR, it's all good, else check the connections.

**TODO - change the command**
Source your workspace, if needed, and don't forget to press on the bottom button near the screen display on the car. Then source the virtual environment and launch the perception process:
```shell
ros2 launch perception_bolide perception.launch.py
```
On another terminal now, source again the virtual environment and run ackermann_controller node:
```shell
ros2 run control_bolide ackermann_controller
```
And to teleoperate with the keyboard open a last terminal and run:
```shell
ros2 run planning_bolide teleop_node
```
Normally, you're good to move the car with the arrows keys of your keyboard. 

## Low level nodes
This repository contains only the low level code for the car and a simple teleop package. Please use another repository to create High-level nodes like a controller for the position, transformation of raw data or a SLAM mechanism.

Normally if we're brave enough, we will try to add a README to all packages, so if you want to have a better explanation of a point try in its folder or code.

### Bolide Interfaces
The [package](./bolide_interfaces/) containing all Messages and Services created for the car. For now, we mainly use messages between topics, the messages are :
- **ForkSpeed** composed of a header and a float32 value corresponding to the speed measures by the fork
- **MultipleRange** composed of 3 Ranges (from std_msgs). One for the Rear left Infrared sensors, one for the right and the last for the Sonar (not used for now)
- **SpeedDirection** composed of two float64 values, one for the speed of the robot and the other for the direction. Both are between -1 and 1.
To access in a python file, you need to import the package (e.g from bolide_interfaces/msg import SpeedDirection)

**If you want to create a Message or a Service for the car please put it in this package and this package only**

### Bolide Direction
The direction of the car is controlled by a Dynamixel plug with a U2D2 connector to the Raspberry Pi. The package [bolide_direction](./bolide_direction/) have a node subscribed to a SpeedDirection message, and send to the dynamixel the angle value needed. The angle is limited by the turning mechanism of the car, so we set a maximum steering angle of 15.5 degrees. To facilitate the process, the direction value of the SpeedDirection message is include in [-1, 1].
The U2D2 port is dynamically connect with the port /dev/ttyU2D2 so you don't need to change the DEVICENAME after every reboot of the car.

### Bolide STM32
The STM32 is the micro-controller connected to the rest of the sensors and the propulsion motor.
The list of sensor used:
- IMU, an 9 DoF accelerometer, gyroscope and yaw sensor used to know the acceleration and turning angle of the car.
- Two infrared sensors to check if there is obstacle behind the car
- A optic fork to determine the speed of the wheel and its sense (forward or backward)
- 
The list of sensor we don't use now but are included:
- A Battery checker to check the voltage of the battery, it seems that it is broke
- A ultrasound sensor, another way to check if there is a obstacle behind the car and its distance, but not used for now

The reception of the sensors data are in the [stm32_node](./bolide_stm32/bolide_stm32/stm32_node.py) and there are on topics.

The micro-controller is also use to send the PWM to the propulsion motor. The [cmd_vel](./bolide_stm32/bolide_stm32/cmd_vel.py) node is a simply node sending the desired PWM value. We send it a cmd value $\in[-1, 1]\cup{2}$ where:
- $cmd = 0$ is the neutral mode, the car is on free wheel and will not stop immediately
- $0.2 < cmd < 1$ is forward
- $-1 < cmd <-0.2$ is backward
- $cmd = 2$ is brake, here the motor will block the rotation of the wheels
**AVOID TO USE 1 and -1 as value, it will decrease the voltage of the RPi5 and shut it off**. To fix this problem we'll need to add a second battery (one for the motors and the other for the RPi5 and other stuffs).
The [stm32_node](./bolide_stm32/bolide_stm32/stm32_node.py) receive the PWM value and will send it to the motor by the D9 pin (if you want to check the value). The PWM value will after be read by the ESC that will send it to the motor. If you think that the ESC is not working correctly please use the [esc_setup.py](TODO file code) code to set it up and read the md file to follow correctly the instructions. TODO 

### Bolide Teleop
This package is for controlling the car manually. For now there is a simple keyboard [teleoperation](./bolide_teleop/bolide_teleop/teleop_keyboard.py) where you can use the arrow of your keyboard to move the car. If you want to add another teleoperation node with a controller or something else, put it here.
The teleop with the keyboard got a incrementation system so if you're backward and you want to go forward you will need to press twice the up arrow. By doing this we assure that we pass by the neutral mode, it is mandatory if you want to avoid crashes of the car.
By doing a teleop with a controller (PS4 controller by exemple) we'll be able to use analogical values and the command will be smoother.

### Sllidar
This package is the official package for our lidar. We use here the sllidar_node to get the data of the lidar. To connect it use the dynamic link /dev/ttyLIDAR to assure the good connection.
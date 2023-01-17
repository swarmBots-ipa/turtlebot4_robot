#!/usr/bin/env python3
# Copyright 2021 Clearpath Robotics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @author Roni Kreinin (rkreinin@clearpathrobotics.com)


from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.conditions import LaunchConfigurationEquals
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.substitutions import Command
from launch_ros.actions import Node
from launch.substitutions import EnvironmentVariable


ARGUMENTS = [
    DeclareLaunchArgument('use_sim', default_value='false',
                          choices=['true', 'false'],
                          description='use_sim'),
    DeclareLaunchArgument('model', default_value='standard',
                          choices=['standard', 'lite'],
                          description='Turtlebot4 Model'),

]


def generate_launch_description():
    # Adding namespace option
    NAMESPACE =  EnvironmentVariable('ROBOT_NAMESPACE', default_value='')
    pkg_turtlebot4_bringup = get_package_share_directory('turtlebot4_bringup')
    pkg_turtlebot4_description = get_package_share_directory(
        'turtlebot4_description')

    xacro_file = PathJoinSubstitution([pkg_turtlebot4_description,
                                       'urdf',
                                       LaunchConfiguration('model'),
                                       'turtlebot4.urdf.xacro'])

    param_file_cmd = DeclareLaunchArgument(
        'param_file',
        default_value=PathJoinSubstitution(
            [pkg_turtlebot4_bringup, 'config', 'turtlebot4.yaml']),
        description='Turtlebot4 Robot param file'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=NAMESPACE,
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim': LaunchConfiguration('use_sim')},
            {'robot_description': Command(
                ['xacro', ' ', xacro_file, ' ', 'gazebo:=ignition'])},
        ],
    )

    turtlebot4_param_yaml_file = LaunchConfiguration('param_file')

    turtlebot4_node = Node(
        package='turtlebot4_node',
        executable='turtlebot4_node',
        namespace=NAMESPACE,
        parameters=[turtlebot4_param_yaml_file,
                    {'model': LaunchConfiguration('model')}],
        output='screen'
    )

    turtlebot4_base_node = Node(
        package='turtlebot4_base',
        executable='turtlebot4_base_node',
        namespace=NAMESPACE,
        parameters=[turtlebot4_param_yaml_file],
        output='screen',
        condition=LaunchConfigurationEquals('model', 'standard')
    )

    rplidar_node = Node(
        name='rplidar_composition',
        package='rplidar_ros',
        executable='rplidar_composition',
        namespace=NAMESPACE,
        output='screen',
        parameters=[{
                'serial_port': '/dev/RPLIDAR',
                'serial_baudrate': 115200,
                'frame_id': 'rplidar_link',
                'inverted': False,
                'angle_compensate': True,
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(robot_state_publisher)
    ld.add_action(rplidar_node)
    ld.add_action(param_file_cmd)
    ld.add_action(turtlebot4_node)
    ld.add_action(turtlebot4_base_node)
    return ld

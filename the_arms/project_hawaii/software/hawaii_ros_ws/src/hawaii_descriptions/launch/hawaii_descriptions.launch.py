# Copyright 2022 Trossen Robotics
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from interbotix_xs_modules.xs_launch import (
    declare_interbotix_xsarm_robot_description_launch_arguments,
)
from interbotix_xs_modules.xs_launch.xs_launch import determine_use_sim_time_param
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    x_spawn = LaunchConfiguration('x_spawn').perform(context)
    y_spawn = LaunchConfiguration('y_spawn').perform(context)
    yaw_spawn = LaunchConfiguration('yaw_spawn').perform(context)
    robot_name_launch_arg = LaunchConfiguration('robot_name').perform(context)
    use_rviz_launch_arg = LaunchConfiguration('use_rviz')
    use_joint_pub_launch_arg = LaunchConfiguration('use_joint_pub')
    use_joint_pub_gui_launch_arg = LaunchConfiguration('use_joint_pub_gui')
    rvizconfig_launch_arg = LaunchConfiguration('rvizconfig')
    robot_description_launch_arg = LaunchConfiguration('robot_description')
    hardware_type_launch_arg = LaunchConfiguration('hardware_type')
    use_gazebo_launch_arg = LaunchConfiguration('gazebo_config')
    using_one_arm = LaunchConfiguration('one_arm').perform(context)

    # sets use_sim_time parameter to 'true' if using gazebo hardware
    use_sim_time_param = determine_use_sim_time_param(
        context=context,
        hardware_type_launch_arg=hardware_type_launch_arg
    )

    namespace = None
    if using_one_arm == 'true':
        namespace = robot_name_launch_arg

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_launch_arg,
            'use_sim_time': use_sim_time_param
        }],
        output={'both': 'log'},
        namespace=namespace
    )

    joint_state_publisher_node = Node(
        condition=IfCondition(use_joint_pub_launch_arg),
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{
            'robot_description': robot_description_launch_arg,
            'use_sim_time': use_sim_time_param   
        }],
        output={'both': 'log'},
    )

    joint_state_publisher_gui_node = Node(
        condition=IfCondition(use_joint_pub_gui_launch_arg),
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output={'both': 'log'},
        namespace=namespace
    )

    rviz2_node = Node(
        condition=IfCondition(use_rviz_launch_arg),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d', rvizconfig_launch_arg,
        ],
        parameters=[{
            'use_sim_time': use_sim_time_param,
        }],
        output={'both': 'log'},
    )

    # gazebo_node = Node(
    #     condition=IfCondition(use_gazebo_launch_arg),
    #     package='gazebo_ros',
    #     executable='spawn_entity.py',
    #     name="spawn_entity",
    #     # namespace=robot_name_launch_arg,
    #     output="screen",
    #     arguments=['-entity',robot_name_launch_arg,
    #     '-robot_namespace', robot_name_launch_arg,          
    #     '-x', x_spawn, '-y', y_spawn, '-Y', yaw_spawn,
    #     '-topic', 'robot_description',
    #     '-timeout', '120.0']
    # )

    return [
        robot_state_publisher_node,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node,
        # gazebo_node,
    ]


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_model',
            default_value='Student_Arm'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_name',
            default_value=LaunchConfiguration('robot_model'),
            description=(
                'name of the robot (typically equal to `robot_model`, but could be anything).'
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            choices=('true', 'false'),
            description='launches RViz if set to `true`.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_joint_pub',
            default_value='false',
            choices=('true', 'false'),
            description='launches the joint_state_publisher node.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_joint_pub_gui',
            default_value='true',
            choices=('true', 'false'),
            description='launches the joint_state_publisher GUI.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'rvizconfig',
            default_value=PathJoinSubstitution([
                FindPackageShare('hawaii_descriptions'),
                'rviz',
                'hawaii.rviz',
            ]),
            description='file path to the config file RViz should load.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'gazebo_config',
            default_value='true',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'x_spawn',
            default_value='0',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'y_spawn',
            default_value='0',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'yaw_spawn',
            default_value='0',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            choices=('true', 'false'),
            description=(
                'tells ROS nodes asking for time to get the Gazebo-published simulation time, '
                'published over the ROS topic /clock.'
            )
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'one_arm',
            default_value='true',
            description='Only launching one arm in total.'
        )
    )
    declared_arguments.extend(
        declare_interbotix_xsarm_robot_description_launch_arguments(),
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg = get_package_share_directory('morphle_stage')
    world = os.path.join(pkg, 'worlds', 'xyz_test.world')
    urdf = os.path.join(pkg, 'urdf', 'xyz_cam', 'xyz_cam.urdf')
    with open(urdf) as f:
        robot_description = f.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world}'}.items())

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        output='screen')

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'morphle_xy_axis'],
        output='screen')

    jsb = Node(
        package='controller_manager', executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen')

    vel = Node(
        package='controller_manager', executable='spawner',
        arguments=['stage_velocity_controller', '--controller-manager', '/controller_manager'],
        output='screen')

    bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/world/xyz_test/model/morphle_xy_axis/link/base_link/sensor/microscope_camera/image'],
        output='screen')

    vision = Node(
        package='morphle_stage',
        executable='vision_detector.py',
        output='screen')

    slider = Node(
        package='morphle_stage',
        executable='xyz_slider_gui.py',
        output='screen')

    return LaunchDescription([
        gazebo, rsp, spawn,
        TimerAction(period=5.0, actions=[jsb, vel]),
        TimerAction(period=8.0, actions=[bridge]),
        TimerAction(period=9.0, actions=[vision]),
        TimerAction(period=10.0, actions=[slider]),
    ])

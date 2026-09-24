import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():
    # Dedicated MAPPING launch: runs FAST-LIO with pcd_save_en (jt128_mapping.yaml) to build a prior
    # map PCD from a bag, then save it on SIGINT. Separate from mapping_mid360.launch.py so the
    # mapping (map-output) and localization runs stay distinct. Default use_sim_time:=true (bag+--clock).
    package_path = get_package_share_directory('fast_lio')
    default_config_path = os.path.join(package_path, 'config', 'jt128_mapping.yaml')
    default_rviz_config_path = os.path.join(package_path, 'rviz_cfg', 'fastlio.rviz')

    feature_extract_enable_param = LaunchConfiguration('feature_extract_enable', default='false')
    point_filter_num_param = LaunchConfiguration('point_filter_num', default='3')
    max_iteration_param = LaunchConfiguration('max_iteration', default='3')
    filter_size_surf_param = LaunchConfiguration('filter_size_surf', default='0.5')
    filter_size_map_param = LaunchConfiguration('filter_size_map', default='0.5')
    cube_side_length_param = LaunchConfiguration('cube_side_length', default='1000.0')
    runtime_pos_log_enable_param = LaunchConfiguration('runtime_pos_log_enable', default='false')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_path = LaunchConfiguration('config_path')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')
    map_file_path = LaunchConfiguration('map_file_path')
    traj_file_path = LaunchConfiguration('traj_file_path')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation clock (bag --clock) if true')
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='FAST-LIO mapping yaml (pcd_save_en=true)')
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='false', description='Use RViz to monitor mapping')
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path, description='RViz config file path')
    # 保存先は launch 引数で可搬に(yaml の /home/user ハードコードを上書き。~ 展開でユーザー非依存)
    declare_map_file_cmd = DeclareLaunchArgument(
        'map_file_path',
        default_value=os.path.expanduser('~/dataset/jt128/jt128_map_telecom2f_fastlio_raw.pcd'),
        description='Ctrl-C 時に保存する累積地図 PCD の出力先')
    declare_traj_file_cmd = DeclareLaunchArgument(
        'traj_file_path',
        default_value=os.path.expanduser('~/dataset/jt128/jt128_telecom2f_fastlio_traj.txt'),
        description='Ctrl-C 時に保存する軌跡(TUM)の出力先。traj[0] = 地図原点姿勢')

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        parameters=[config_path,
                    {'use_sim_time': use_sim_time,
                     'feature_extract_enable': feature_extract_enable_param,
                     'point_filter_num': point_filter_num_param,
                     'max_iteration': max_iteration_param,
                     'filter_size_surf': filter_size_surf_param,
                     'filter_size_map': filter_size_map_param,
                     'cube_side_length': cube_side_length_param,
                     'runtime_pos_log_enable': runtime_pos_log_enable_param,
                     'map_file_path': map_file_path,
                     'traj_save.traj_file_path': traj_file_path}],
        output='screen')
    rviz_node = Node(
        package='rviz2', executable='rviz2', arguments=['-d', rviz_cfg],
        condition=IfCondition(rviz_use))

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_config_path_cmd)
    ld.add_action(declare_rviz_cmd)
    ld.add_action(declare_rviz_config_path_cmd)
    ld.add_action(declare_map_file_cmd)
    ld.add_action(declare_traj_file_cmd)
    ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)
    return ld

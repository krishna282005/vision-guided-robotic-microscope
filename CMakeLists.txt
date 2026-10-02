cmake_minimum_required(VERSION 3.8)
project(morphle_stage)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf config launch worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/vision_detector.py
    scripts/xyz_slider_gui.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

---
author: admin@pldz1.com
category: ros2
date: '2025-01-01'
serialNo: 101
status: publish
summary: ROS2和Arduino通讯的介绍, 两个通讯可能实现的方式.
tags:
- ROS2和单片机
thumbnail: /api/v1/website/image/ros2/1_ros2_arduino_thumbnail.jpg
title: ROS2 和 Arduino 通讯
---

ROS2 和 Arduino 的通讯方式有很多，个人觉得只要分为两大类

1. 第一类是采用 ros2arduino 或者 MicroROS 这类的包，在 arduino 板卡上尝试直接进行 ros2 的节点的发布和订阅, 然后主机上则采用对应的 DDS 工具 例如 MicroROS 的各种通讯中间件，Mirco_XRCE_DDS 图像中间件，或者是 ros2_serial 获取发布订阅的串口数据的中间件

2. 直接从微控制器本身出发，Arduino 直接烧录自身的功能代码 而不依赖仍和 ROS2 相关的库，然后用 Python 或者 C/C++编写接受串口消息的节点，做发布和订阅

![1_different_com_method](/api/v1/website/image/ros2/1_different_com_method.png)

那么这里就采用第二种方式，最简单快速的完成 ROS2 和 Arduino 的通讯
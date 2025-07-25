---
author: admin@pldz1.com
category: ros2
date: '2025-01-01'
serialNo: 1
status: publish
summary: ROS2的下载和安装和ROS2是什么的介绍.
tags:
- ROS2基础
thumbnail: /api/v1/website/image/ros2/1_ros2_ubuntu_thumbnail.jpg
title: Ubuntu配置与ROS2快速体验
---

# 1.1 Ubuntu 配置与 ROS2 安装

## 1.1.1 Ubuntu22.04 安装

1. 下载 Ubuntu22.04：本文选择 [中科大镜像网](https://mirrors.ustc.edu.cn/) ，选择 Ubuntu22.04 镜像下载，后续放入 VMware 进行 **断网安装**

![下载镜像](/api/v1/website/image/ros2/1_download_ubuntu_mirror.png)

> VMware15 链接：
> 链接：https://pan.baidu.com/s/1BbaGtDhjVXCWeS2vuk3bRw
> 提取码：7lzk 复制这段内容后打开百度网盘手机 App，操作更方便哦

2. Ubuntu22.04 换源：将桌面版本的 Ubuntu 的软件更新设置来源为国内的镜像，或者直接输入命令`sudo gedit /etc/apt/sources.list`将内容改为如下所示：

```shell
deb https://mirrors.ustc.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-proposed main restricted universe multiverse
deb-src https://mirrors.ustc.edu.cn/ubuntu/ jammy-proposed main restricted universe multiverse
```

![Ubuntu换源](/api/v1/website/image/ros2/1_change_apt_source.png)

## 1.1.2 下载安装 ROS2

1. 输入命令`sudo apt-get update -y`对软件源进行更新，输入`sudo apt-get upgrade -y`对软件进行更新：

```shell
sudo apt-get update -y && sudo apt-get upgrade -y
```

2. 获取 ROS2 的秘钥，并 ROS2 的存储库添加到源列表：

```shell
sudo apt install curl gnupg lsb-release && sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

3. 如果出现关于 `raw.githubusercontent.com` 连接失败的处理

- 1. 访问 `https://tool.lu/ip/` 并输入域名 `raw.githubusercontent.com`，查询 ip 地址，这里查询到的是 `185.199.108.133`

![IP地址查询](/api/v1/website/image/ros2/1_request_ip_address.png)

- 2. 修改 `sudo gedit /etc/hosts`文件,并手动添加 DNS 解析：

![手动添加IP](/api/v1/website/image/ros2/1_modify_dns_information.png)

4. 下载 ROS2-humble：更新软件到最新版本，然后下载 ROS2-humble：

```shell
sudo apt-get update -y && sudo apt-get upgrade -y

sudo apt install ros-humble-desktop
```

5. 安装 colcon 构建工具： 不同于之前 ROS1 的 catkin 工具，ROS2 用 colcon 进行包的构建：`sudo apt install python3-colcon-common-extensions`

## 1.1.3 配置 ROS2 环境并测试

1. 配置 ROS2 环境： 默认 ROS2-humble 安装在`/opt/ros/humble/`下，将 ROS2 的环境添加到用户环境文件`~/.bashrc`中，输入`echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc`

2. 测试 ROS2：`ros2 run turtlesim turtlesim_node`和`ros2 run turtlesim turtle_teleop_key`运行小乌龟

![小乌龟测试程序](/api/v1/website/image/ros2/1_download_ubuntu_mirror.png)

# 1.2 使用 VSCode 搭建 ROS2 开发环境

## 1.2.1 安装并配置 VSCode

1. 安装 VSCode: [VSCode 下载地址](https://code.visualstudio.com/Download)，持续下一步即可安装完成。

2. 下载完成后安装 VSCode 插件：插件主要包括 `C/C++` 和 `Python` 以及 `CMake` 的插件，如下图所示：

![VSCode插件](/api/v1/website/image/ros2/1_download_vscode_ros2_plugin.png)

## 1.2.2 创建 ROS2 工程的方法

1. ROS2 create 命令：通过 `ros2 pkg create --help` 熟悉创建 ROS2 项目的方法

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter$ ros2 pkg create --help
usage: ros2 pkg create [-h] [--package-format {2,3}] [--description DESCRIPTION] [--license LICENSE]
                       [--destination-directory DESTINATION_DIRECTORY] [--build-type {cmake,ament_cmake,ament_python}]
                       [--dependencies DEPENDENCIES [DEPENDENCIES ...]] [--maintainer-email MAINTAINER_EMAIL]
                       [--maintainer-name MAINTAINER_NAME] [--node-name NODE_NAME] [--library-name LIBRARY_NAME]
                       package_name

Create a new ROS 2 package

positional arguments:
  package_name          The package name

options:
  -h, --help            show this help message and exit
  --package-format {2,3}, --package_format {2,3}
                        The package.xml format.
  --description DESCRIPTION
                        The description given in the package.xml
  --license LICENSE     The license attached to this package; this can be an arbitrary string, but a LICENSE file will only
                        be generated if it is one of the supported licenses (pass '?' to get a list)
  --destination-directory DESTINATION_DIRECTORY
                        Directory where to create the package directory
  --build-type {cmake,ament_cmake,ament_python}
                        The build type to process the package with
  --dependencies DEPENDENCIES [DEPENDENCIES ...]
                        list of dependencies
  --maintainer-email MAINTAINER_EMAIL
                        email address of the maintainer of this package
  --maintainer-name MAINTAINER_NAME
                        name of the maintainer of this package
  --node-name NODE_NAME
                        name of the empty executable
  --library-name LIBRARY_NAME
                        name of the empty library
```

下面对上诉的命令进行简单的介绍：

> - 提示当中的`[]`的内容表示命令关键字，`{}`的内容表示可以携带的参数示例，例如创建 `--build-type` 后面就可以接着 `ament_cmake` 参数
> - `[--destination-directory DESTINATION_DIRECTORY]` ：ROS2 的项目的位置，即在哪里创建你的 ROS2 项目
> - `[--build-type {cmake,ament_cmake,ament_python}]` ：ROS2 编译项目的方式，有`cmake` `ament_camke`和`ament_python`三种可选，`ament_cmake`是基于 cmake 的一个 cmake 升级工具， 了解更多的 ROS2 ament 工具：[(https://blog.csdn.net/gongdiwudu/article/details/126192244)](<(https://blog.csdn.net/gongdiwudu/article/details/126192244)>)
> - `[--dependencies]` ：ROS2 项目的依赖项，这部分内容后面可以手动增加，其中常见的`rclpy 是 python`的节点依赖项，`rclcpp是C/C++节点的依赖项`，（`rcl`表示`ros2 client`）
> - `[--node-name]` ：预先设置的 ROS2 节点名字

2. 因此可以使用命令：`ros2 pkg create <你的项目名字> --build-type <选择cmake/ament_camke/ament_python三者之一作为项目的编译工具> --node-name <节点名称，这一项可以不写，后续手动配置> --dependencies <依赖项名字，例如在ROS1中常用的rclpy rclcpp std_msgs sensor_msgs等>`，如：

> Tips：这里补充还是推荐才有下划线割开的功能包命名方法而不是大小写混合，否则会出错
>
> ![命名的问题](/api/v1/website/image/ros2/1_node_name_build_warning.png)

```shell
ros2 pkg create demo --build-type ament_cmake --node-name demo_node --dependencies rclcpp
```

## 1.2.3 使用 VSCode 创建 ROS2 的 C/C++项目

1. 创建 ROS2 C++工程：`ros2 pkg create vscodeCppDemo --build-type ament_cmake --node-name vscodeCppDemoNode --dependencies rclcpp std_msgs`

> Tips：这里补充还是推荐才有下划线割开的功能包命名方法而不是大小写混合，否则会出错
>
> ![命名的问题](/api/v1/website/image/ros2/1_node_name_build_warning.png)

2. 查看工程目录结构：`tree . `，可以发现在`src`目录下 **存在了节点名称的 cpp 文件** ，即 ROS2 项目已经构建了配置好节点内容的工程

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ros2 pkg create vscodeCppDemo --build-type ament_cmake --node-name vscodeCppDemoNode --dependencies rclcpp std_msgs
going to create a new package
package name: vscodeCppDemo
destination directory: /mnt/hgfs/VMware/ROS2_DEMO/1_Chapter/code
package format: 3
version: 0.0.0
description: TODO: Package description
maintainer: ['pldz <pldz@R7000.com>']
licenses: ['TODO: License declaration']
build type: ament_cmake
dependencies: ['rclcpp', 'std_msgs']
node_name: vscodeCppDemoNode
creating folder ./vscodeCppDemo
creating ./vscodeCppDemo/package.xml
creating source and include folder
creating folder ./vscodeCppDemo/src
creating folder ./vscodeCppDemo/include/vscodeCppDemo
creating ./vscodeCppDemo/CMakeLists.txt
creating ./vscodeCppDemo/src/vscodeCppDemoNode.cpp

[WARNING]: Unknown license 'TODO: License declaration'.  This has been set in the package.xml, but no LICENSE file has been created.
It is recommended to use one of the ament license identitifers:
Apache-2.0
BSL-1.0
BSD-2.0
BSD-2-Clause
BSD-3-Clause
GPL-3.0-only
LGPL-3.0-only
MIT
MIT-0

pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ tree .
.
└── vscodeCppDemo
    ├── CMakeLists.txt
    ├── include
    │   └── vscodeCppDemo
    ├── package.xml
    └── src
        └── vscodeCppDemoNode.cpp

4 directories, 3 files
```

3. 在`<ROS2工程目录下>/src/<节点cpp>.cpp`进行节点编程，ROS2 是 C++14 的编程风格：

```cpp
#include "rclcpp/rclcpp.hpp"

// 继承ROS2的客户端节点
class VSCodeCppDemo: public rclcpp::Node{
public:
    // ROS2节点的构造函数
    VSCodeCppDemo(const char* nodeName):Node(nodeName){
        RCLCPP_INFO(this->get_logger(),"hello world!");
    }

};

int main(int argc, char *argv[])
{
    rclcpp::init(argc,argv);
    // 生成自定义的ROS2客户端对象, node是一个对象指针
    auto node = std::make_shared<VSCodeCppDemo>("vscodeCppDemoNode");
    rclcpp::shutdown();
    return 0;
}
```

4. 针对 VSCode 的`settings.json`进行配置：在项目下面新建 `.vscode` 文件夹，然后在在该文件夹下新建 `settings.json` , 添加下列内容：

```json
{
  // Settings.json的配置，主要在于添加/opt/ros/humble文件夹下的ros2的include路径

  // pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code/.vscode$ tree .
  // .
  // └── settings.json
  // 0 directories, 1 file

  "files.associations": {
    "cstdio": "cpp"
  },
  "C_Cpp.default.includePath": ["/opt/ros/humble/include/**"]
}
```

![VSCode Settings配置](/api/v1/website/image/ros2/1_config_vscode_settings.gif)

5. 配置 ROS2 项目的 `package.xml` 文件：`package.xml` 文件是 ROS2 项目的功能包管理文件，下面添加了一点注释：

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>vscodeCppDemo</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <!-- 包的作者信息,主要来自Git的配置 -->
  <maintainer email="pldz@R7000.com">pldz</maintainer>
  <license>TODO: License declaration</license>

  <!-- 编译工程的工具 -->
  <buildtool_depend>ament_cmake</buildtool_depend>

  <!-- 编译需要的依赖项,可以手动添加 -->
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

6. 配置 `CMakeLists.txt` 文件：`CMakeLists.txt` 是 ROS2 项目的编译配置文件，ROS2 项目采用 ament_cmake 工具，需要配置的包括以下 6 部分内容：

```cpp
find_package()                  // 1. 列出依赖项，通俗的说是项目编译所需要的全部依赖项名称，节点和项目是两个概念，一个项目可以有多个节点
add_executable()                // 2. 可执行文件的路径，通俗来说是编译节点的main函数入口
target_include_directories()    // 3. 编译节点所需要的include的位置
ament_target_dependencies()     // 4. 编译节点所需要的依赖项，这一步的目的是连接编译该节点所需要的依赖项
install()                       // 5. 通俗来说，是将编译好的节点给拷贝到ROS功能包的目录，使得能够通过指令ros2 run <包名> <节点名>的配置，默认这一步的目的就是将build文件夹的内容拷贝到install的lib文件夹下
ament_package()                 // 6. 生成ament工具的环境，缺少这一步，无法在install文件夹下生成setup.bash文件等等
```

下面添加了一点注释：

```cpp
cmake_minimum_required(VERSION 3.8)
project(vscodeCppDemo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 1. find dependencies, 这里可以引入外部依赖包
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# 2. 节点(也叫可执行文件)的映射
add_executable(vscodeCppDemoNode src/vscodeCppDemoNode.cpp)

# 3. Include文件的位置
target_include_directories(vscodeCppDemoNode PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

# 4. 目标依赖库
target_compile_features(vscodeCppDemoNode PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17
ament_target_dependencies(
  vscodeCppDemoNode
  "rclcpp"
  "std_msgs"
)

# 5. 安装规则
install(TARGETS vscodeCppDemoNode
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# 6. ament工具的功能包整理
ament_package()

```

7. 利用 `colcon` 工具构建项目：在项目的工程目录下，输入`colcon build`进行构建

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ colcon build
WARNING: Package name "vscodeCppDemo" does not follow the naming conventions. It should start with a lower case letter and only contain lower case letters, digits, underscores, and dashes.
Starting >>> vscodeCppDemo
--- stderr: vscodeCppDemo
WARNING: Package name "vscodeCppDemo" does not follow the naming conventions. It should start with a lower case letter and only contain lower case letters, digits, underscores, and dashes.
---
Finished <<< vscodeCppDemo [8.27s]

Summary: 1 package finished [8.62s]
  1 package had stderr output: vscodeCppDemo
```

8. 执行该项目节点文件：

- 1. 尝试手动执行，在项目目录下的 `build/<ROS2项目名称>` 下存放着项目节点 `ROS2项目节点`，直接运行该文件：如下所示

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ./build/vscodeCppDemo/vscodeCppDemoNode
[INFO] [1682264164.879460585] [helloworld_node]: hello world!
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ file ./build/vscodeCppDemo/vscodeCppDemoNode
./build/vscodeCppDemo/vscodeCppDemoNode: ELF 64-bit LSB pie executable, x86-64, version 1 (GNU/Linux), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=53b5061fab0864a3b53f587b0cbc8a6be1d342f1, for GNU/Linux 3.2.0, not stripped
```

- 2. 通过 ROS2 运行节点：首先需要添加项目的 install 环境，即 `source <项目目录>/install/setup.bash`，然后可以通过`ros2 run <项目名称> <节点名称>` 运行节点

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ source ./install/setup.bash
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ros2 run vscodeCppDemo vscodeCppDemoNode
[INFO] [1682264459.635230302] [helloworld_node]: hello world!
```

9. ROS2 的 C/C++项目的目录结构：在项目目录下输入`tree -L 3` 查看最多三级文件结构，其中：

- 1. `build`文件夹：存储编译的文件和可执行的 ROS2 节点

- 2. `install`文件夹：直接反应叫安装目录，包括能够通过 `ros2 run ...` 指令运行 ROS2 节点的环境

- 3. `log`文件夹：存储日志文件

- 4. `<项目名的文件夹>`：存放 ROS2 项目的源码，其中的 `package.xml`配置包信息（包名、版本、作者、依赖项）；`CMakeLists.txt` 用于配置编译规则（源文件位置，编译所要连接的依赖项等等）；

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ tree -L 3
.
├── build
│   ├── COLCON_IGNORE
│   └── vscodeCppDemo
│       ├── ament_cmake_core
│       ├── ament_cmake_environment_hooks
│       ├── ... 这里手动省略
│       ├── Makefile
│       └── vscodeCppDemoNode
├── install
│   ├── COLCON_IGNORE
│   ├── local_setup.bash
│   ├── ... 这里手动省略
│   ├── setup.bash
│   └── vscodeCppDemo
│       ├── lib
│       └── share
├── log
│   ├── build_2023-04-23_23-31-44
│   │   ├── events.log
│   │   ├── logger_all.log
│   │   └── vscodeCppDemo
│   └── COLCON_IGNORE
└── vscodeCppDemo
    ├── CMakeLists.txt
    ├── include
    │   └── vscodeCppDemo
    ├── package.xml
    └── src
        └── vscodeCppDemoNode.cpp

23 directories, 30 files
```

## 1.2.4 使用 VSCode 创建 ROS2 的 Python 项目

1. 创建 ROS2 的 Python 项目：`ros2 pkg create vscodePythonDemo --build-type ament_python --dependencies rclpy std_msgs --node-name vscodePythonDemoNode`，其中依赖项与 C/C++的节点不同是`rclpy`，此时在项目的同名目录下，已经有了`节点.py`文件

> Tips：这里补充还是推荐才有下划线割开的功能包命名方法而不是大小写混合，否则会出错
>
> ![命名的问题](/api/v1/website/image/ros2/1_node_name_build_warning.png)

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ros2 pkg create vscodePythonDemo --build-type ament_python --dependencies rclpy std_msgs --node-name vscodePythonDemoNode
going to create a new package
package name: vscodePythonDemo
destination directory: /mnt/hgfs/VMware/ROS2_DEMO/1_Chapter/code
package format: 3
version: 0.0.0
description: TODO: Package description
maintainer: ['pldz <pldz@R7000.com>']
licenses: ['TODO: License declaration']
build type: ament_python
dependencies: ['rclpy', 'std_msgs']
node_name: vscodePythonDemoNode
creating folder ./vscodePythonDemo
creating ./vscodePythonDemo/package.xml
creating source folder
creating folder ./vscodePythonDemo/vscodePythonDemo
creating ./vscodePythonDemo/setup.py
creating ./vscodePythonDemo/setup.cfg
creating folder ./vscodePythonDemo/resource
creating ./vscodePythonDemo/resource/vscodePythonDemo
creating ./vscodePythonDemo/vscodePythonDemo/__init__.py
creating folder ./vscodePythonDemo/test
creating ./vscodePythonDemo/test/test_copyright.py
creating ./vscodePythonDemo/test/test_flake8.py
creating ./vscodePythonDemo/test/test_pep257.py
creating ./vscodePythonDemo/vscodePythonDemo/vscodePythonDemoNode.py

[WARNING]: Unknown license 'TODO: License declaration'.  This has been set in the package.xml, but no LICENSE file has been created.
It is recommended to use one of the ament license identitifers:
Apache-2.0
BSL-1.0
BSD-2.0
BSD-2-Clause
BSD-3-Clause
GPL-3.0-only
LGPL-3.0-only
MIT
MIT-0
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ cd vscodePythonDemo/
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code/vscodePythonDemo$ tree .
.
├── package.xml
├── resource
│   └── vscodePythonDemo
├── setup.cfg
├── setup.py
├── test
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
└── vscodePythonDemo
    ├── __init__.py
    └── vscodePythonDemoNode.py

3 directories, 9 files
```

2. 创建一个简单的 ROS2 的 Python 节点：代码如下，基本内容见注释

```py
import rclpy
from rclpy.node import Node

# 继承Node类，定义VSCodePythonDemo类
class VSCodePythonDemo(Node):
    # 初始化Python构造函数
    def __init__(self, nodeName:str):
        super().__init__(nodeName)

    def printHello(self):
        self.get_logger().info("hello world!")

def main():
    rclpy.init()
    # 创建VSCodePythonDemo对象
    node = VSCodePythonDemo("vscodePythonDemo")
    # 调用成员函数
    node.printHello()
    rclpy.shutdown()
```

3. Python 的 VSCode 环境配置：默认情况下 VSCode 的 Python 解析器，能够定位到`rclpy.py`的位置在`/opt/ros/humble/local/lib/python3.10/dist-packages/`下，如果无法找到，可以手动配置`.vscode` 文件夹下的 `settings.json`文件，加入`"python.analysis.extraPaths": ["/opt/ros/humble/local/lib/python3.10/dist-packages/"],`，这样的配置同样能够将自己安装的的 Python 依赖项加入到 vscode 的开发环境中

![Python项目的VSCode配置](/api/v1/website/image/ros2/1_config_python_vscode_env.png)

4. ROS2 的 Python 项目的简单配置：与 C/C++项目不同，Python 项目主要配置`packages.xml`文件来管理依赖项和 Python 包，`setup.py`主要给 Python 项目进行打包配置

- 1. `packages.xml`文件的简单注释：

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>vscodePythonDemo</name>
  <version>0.0.0</version>
  <!-- 包的作者信息,主要来自Git的配置 -->
  <description>TODO: Package description</description>
  <maintainer email="pldz@R7000.com">pldz</maintainer>
  <license>TODO: License declaration</license>

  <!-- 编译需要的依赖项,可以手动添加 -->
  <depend>rclpy</depend>
  <depend>std_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

- 2. `setup.py`文件的简单注释：

```py
from setuptools import setup

# 项目包名
package_name = 'vscodePythonDemo'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    # 依赖的打包工具
    install_requires=['setuptools'],
    zip_safe=True,
    # 项目用户信息
    maintainer='pldz',
    maintainer_email='pldz@R7000.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 可执行文件的入口
            'vscodePythonDemoNode = vscodePythonDemo.vscodePythonDemoNode:main'
        ],
    },
)

```

5. 编译 ROS2 的 Python 项目：在项目目录下，输入：`colcon build`，利用`ament_python`工具构建 Python 项目

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ colcon build
WARNING: Package name "vscodeCppDemo" does not follow the naming conventions. It should start with a lower case letter and only contain lower case letters, digits, underscores, and dashes.
WARNING: Package name "vscodePythonDemo" does not follow the naming conventions. It should start with a lower case letter and only contain lower case letters, digits, underscores, and dashes.
Starting >>> vscodeCppDemo
Starting >>> vscodePythonDemo
--- stderr: vscodePythonDemo
/usr/lib/python3/dist-packages/setuptools/command/install.py:34: SetuptoolsDeprecationWarning: setup.py install is deprecated. Use build and pip and other standards-based tools.
  warnings.warn(
---
Finished <<< vscodePythonDemo [1.41s]
Finished <<< vscodeCppDemo [1.79s]

Summary: 2 packages finished [2.10s]
  1 package had stderr output: vscodePythonDemo
```

> 注意此时出现的`SetuptoolsDeprecationWarning: setup.py install is deprecated. Use build and pip and other standards-based tools.`主要是因为`setuptools`的版本和 ROS2 所需要的版本不一致，但是不会影响编译

1. 运行 ROS2 的 Python 项目：`.py`文件本身就是一个可执行的脚本，如果 Python 解析器的环境依赖都能够被找到的话，可以直接输入`python3 xx.py`运行文件，同样通过激活`./install/setup.bash`文件，利用 ROS2 运行 Python 节点

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ python3 ./build/vscodePythonDemo/build/lib/vscodePythonDemo/vscodePythonDemoNode.py
[INFO] [1682341866.812861345] [helloworld_py_node]: hello world!
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ python3 ./vscodePythonDemo/vscodePythonDemo/vscodePythonDemoNode.py
[INFO] [1682341890.895240693] [helloworld_py_node]: hello world!
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ros2 run vscodePythonDemo/ --prefix
build/             install/           log/               .vscode/           vscodeCppDemo/     vscodePythonDemo/
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ source ./install/setup.bash
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ros2 run vscodePythonDemo
--prefix              vscodePythonDemoNode
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ ros2 run vscodePythonDemo vscodePythonDemoNode
[INFO] [1682341946.345360821] [helloworld_py_node]: hello world!
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$
```

7. ROS2 的 Python 项目的简单文件结构：在项目文件夹下输入`tree -L 3`查看项目三级目录；其中的`setup.cfg是功能包基本配置文件`，它的作用会影响项目`.build`文件夹下对 Python 项目的配置。

```shell
pldz@pldz-pc:~/share/ROS2_DEMO/1_Chapter/code$ tree -L 3
.
├── build
│   ├── COLCON_IGNORE
│   ├── vscodeCppDemo
| ... 手动删除了C/C++项目的内容
└── vscodePythonDemo
    ├── package.xml
    ├── resource
    │   └── vscodePythonDemo
    ├── setup.cfg
    ├── setup.py
    ├── test
    │   ├── test_copyright.py
    │   ├── test_flake8.py
    │   └── test_pep257.py
    └── vscodePythonDemo
        ├── __init__.py
        └── vscodePythonDemoNode.py
```

# 1.3 ROS2 的基本体系

## 1.3.1 ROS2 架构

ROS2 的介绍中，有这么一张图，习惯划分说 ROS2 分为三层[来源于 B 站 UP](https://www.bilibili.com/video/BV1HD4y1q7UH/)：

![ROS2架构](/api/v1/website/image/ros2/1_ros2_structure.png)

1. 操作系统层（OS Layer）：如前所述，ROS 虽然称之为机器人操作系统，但实质只是构建机器人应用程序的软件开发工具包，ROS 必须依赖于传统意义的操作系统，目前 ROS2 可以运行在 Linux、Windows、Mac 或 RTOS 上。

2. 中间层（Middleware Layer）：主要由数据分发服务 DDS 与 ROS2 封装的关于机器人开发的中间件组成。DDS 是一种去中心化的数据通讯方式，ROS2 还引入了服务质量管理 （Quality of Service）机制，借助该机制可以保证在某些较差网络环境下也可以具备良好的通讯效果。ROS2 中间件则主要由客户端库、DDS 抽象层与进程内通讯 API 构成。

3. 应用层（Application Layer）：是指开发者构建的应用程序，在应用程序中是以功能包为核心的，在功能包中可以包含源码、数据定义、接口等内容。

## 1.3.2 ROS2 和 ROS1 的区别

老生常谈的一个话题了，总结来说：

1. 协议不一样：ROS1 用的是 TCP 和 UDP 协议，而 ROS2 用 DDS 协议；DDS 是 ROS2 的一个很重要的概念，DDS 是专用总线协议，速度更快更可靠；

2. 架构不一样，ROS1 通过 ROS Master 管理节点，而 ROS2 是分布式通讯架构，不需要 ROS Master

3. ROS2 支持的平台更多，能够支撑嵌入式开发板，实时操作系统 RTOS 等平台

## 1.3.3 ROS2 应用方向

1. Nav2 项目：Nav2 项目继承自 ROS Navigation Stack。该项目旨在可以让移动机器人从 A 点安全的移动到 B 点。它也可以应用于涉及机器人导航的其他应用，例如跟随动态点。Nav2 将用于实现路径规划、运动控制、动态避障和恢复行为等一系列功能

2. microROS：在基于 ROS 的机器人应用中，micro-ROS 正在弥合性能有限的微控制器和一般处理器之间的差距。micro-ROS 在各种嵌入式硬件上运行，使 ROS 能直接应用于机器人硬件

# 1.4 总结和参考内容

## 1.4.1 总结

1. 创建 ROS2 项目的流程：

> - 1. 创建功能包: `ros2 pkg create <项目名> --build-type <cmake/ament_camke/ament_python> --node-name <节点名> --dependencies <rclpy/rclcpp ...>`
> - 2. 编辑源文件：采用继承`rcl`节点发方式，创建 ROS2 节点
> - 3. 编辑配置文件： C/C++ 配置`packages.xml`和`CMakeLists.txt`分别进行依赖项管理和编译配置，Python 项目配置`packages.xml`和`setup.py`分别进行依赖项和编译安装配置
> - 4. 编译：安装`colcon`工具，`sudo apt install python3-colcon-common-extensions`，**并且在项目目录下**，进行`colcon build`
> - 5. 执行：激活项目环境`source <项目>/install/setup.bash`，然后输入`ros2 run <package> <node>`

## 1.4.2 参考内容

- 1. [【ROS2 原理 3】：构建系统“ament_cmake”和构建工具“ament_tools”](https://blog.csdn.net/gongdiwudu/article/details/126192244)
- 2. [ROS2 学习笔记（五）-- ROS2 命令行操作常用指令总结（一）](https://blog.csdn.net/aibingjin/article/details/123899829)
- 3. [Developing a ROS 2 package](https://docs.ros.org/en/foxy/How-To-Guides/Developing-a-ROS-2-Package.html)
- 4. [C++日志（三十一）类继承时的构造函数](https://zhuanlan.zhihu.com/p/106920426)
- 5. [ROS2 API](https://docs.ros2.org/latest/api/)
- 6. [ROS2 中文网](http://dev.ros2.fishros.com/)
- 7. [ROS2.0 整体架构说明](https://blog.csdn.net/xmy306538517/article/details/78770788)
- 8. [ROS 2 Design](https://design.ros2.org/)
# 🛠️ 安装指南  

## 1. 环境要求  
| 依赖项       | 作用                     | 版本要求       |
|--------------|--------------------------|----------------|
| Python       | 运行核心逻辑             | ≥3.8           |
| CMake        | 构建C++扩展             | ≥3.10          |
| C++编译器    | 编译高性能模块           | GCC/Clang/MSVC |
| OpenCV       | 虚拟摄像头支持           | ≥4.5           |  


## 2. 平台特定安装  

### ✅ Ubuntu/Debian  
```bash
# 系统依赖
sudo apt update && sudo apt install -y python3 python3-pip cmake g++ libopencv-dev
# Python依赖
pip3 install -r requirements.txt
```
## ✅ macOS（Homebrew）
```bash
# 系统依赖
brew install python cmake opencv
# Python依赖
pip install -r requirements.txt
```

## ✅ Windows（MinGW）
### 1.安装 [Python](https://www.python.org/downloads/)
### 2.安装 [CMake](https://cmake.org/download/)
### 3.安装 [MinGW](https://sourceforge.net/projects/mingw/)
### 4.运行：
```bash
pip install -r requirements.txt
```
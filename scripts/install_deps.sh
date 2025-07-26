#!/bin/bash
# scripts/install_deps.sh
#!/bin/bash

# 安装依赖
echo "正在安装依赖..."

# 检查操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-dev cmake g++ libopencv-dev
    pip3 install -r requirements.txt

elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install python3 cmake opencv
    pip3 install -r requirements.txt

elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows
    # 假设已安装Python、CMake和MinGW
    pip install -r requirements.txt
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "依赖安装完成"
#!/bin/bash
# scripts/build_extensions.sh
#!/bin/bash

# 构建C++扩展模块
echo "正在构建C++扩展模块..."

# 检查操作系统
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux/macOS
    # 构建相机模块
    cd src/ext/camera_module
    mkdir -p build
    cd build
    cmake ..
    make
    cd ../../../..

    # 构建APK加载器模块
    cd src/ext/apk_loader
    mkdir -p build
    cd build
    cmake ..
    make
    cd ../../../..

elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows
    # 构建相机模块
    cd src/ext/camera_module
    mkdir -p build
    cd build
    cmake -G "MinGW Makefiles" ..
    mingw32-make
    cd ../../../..

    # 构建APK加载器模块
    cd src/ext/apk_loader
    mkdir -p build
    cd build
    cmake -G "MinGW Makefiles" ..
    mingw32-make
    cd ../../../..
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "C++扩展模块构建完成"
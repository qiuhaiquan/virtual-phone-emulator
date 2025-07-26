# docs/README.md
# 虚拟手机模拟器

虚拟手机模拟器是一个能够在计算机上模拟手机环境并执行APK文件的开源项目。它可以检测计算机硬件并将其虚拟化为手机硬件，允许Android应用调用这些虚拟硬件资源。

## 特点

- 检测并虚拟计算机硬件为手机硬件
- 支持执行APK文件
- 跨平台支持（Windows、Linux、macOS）
- 模块化设计，易于扩展
- 支持多种编程语言（Python、C++、Java）
- 提供控制台和图形界面

## 安装

1. 克隆仓库
```bash
git clone https://github.com/doubao/virtual-phone-emulator.git
cd virtual-phone-emulator
```
## 构建扩展模块
```bash
./scripts/build_extensions.sh
```

## 运行模拟器
```bash
python src/__main__.py --gui  # 图形界面
python src/__main__.py        # 控制台界面
```

## 📖 文档  
- [安装指南](./INSTALL.md)  
- [使用教程](./USAGE.md)  
- [API 参考](./API_REFERENCE.md)  
- [贡献指南](./CONTRIBUTING.md)  


## 🤝 贡献  
欢迎通过提交问题、拉取请求或提供反馈来贡献代码！请阅读[贡献指南](./CONTRIBUTING.md)了解更多信息。  
# setup.py
from setuptools import setup, find_packages

setup(
    name='virtual-phone-emulator',
    version='0.1.0',
    description='一个能够模拟手机环境并执行APK文件的虚拟手机模拟器',
    author='Doubao',
    author_email='doubao@example.com',
    url='https://github.com/doubao/virtual-phone-emulator',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'opencv-python',  # 用于相机模拟
        'pyjnius',        # 用于Java集成
        'numpy',          # 用于图像处理
        'PyQt5',          # 用于图形界面
    ],
    entry_points={
        'console_scripts': [
            'virtual-phone=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
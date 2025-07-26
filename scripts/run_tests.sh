#!/bin/bash
# scripts/run_tests.sh
#!/bin/bash

# 运行测试
echo "正在运行测试..."

# 设置Python路径
export PYTHONPATH=$(pwd)/src

# 运行所有测试
python -m unittest discover -s tests -p "test_*.py"

echo "测试完成"
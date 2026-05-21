#!/usr/bin/env python3
import os
import sys

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ali_data_dir = os.path.join(current_dir, 'AliData')
sys.path.insert(0, ali_data_dir)

print(f"Python路径: {sys.path}")

try:
    import schedule
    print("✓ schedule模块导入成功")
except ImportError as e:
    print(f"✗ schedule模块导入失败: {e}")
    sys.exit(1)

try:
    import xlrd
    print("✓ xlrd模块导入成功")
except ImportError as e:
    print(f"✗ xlrd模块导入失败: {e}")
    sys.exit(1)

try:
    import requests
    print("✓ requests模块导入成功")
except ImportError as e:
    print(f"✗ requests模块导入失败: {e}")
    sys.exit(1)

# 尝试导入wxwork相关的模块
try:
    hooks_dir = os.path.join(ali_data_dir, 'hooks')
    sys.path.insert(0, hooks_dir)
    
    from manager.cloth_trade_manager import ClothTradeManager
    print("✓ ClothTradeManager导入成功")
except Exception as e:
    print(f"✗ ClothTradeManager导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ 所有依赖验证通过！")

"""Quick test for mmumu - minimal dependencies."""
import sys
import os

print("=" * 60)
print("MMUMU 快速测试")
print("=" * 60)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test 1: Import
print("\n[1/5] 测试导入...")
try:
    from mmumu.base import get_mumu_path
    from mmumu.manager import MuMuManager
    from mmumu.api import MuMuApi
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# Test 2: Get path
print("\n[2/5] 测试路径检测...")
try:
    path = get_mumu_path()
    print(f"✅ 找到 MuMu: {path}")
    print(f"   路径存在: {os.path.exists(path)}")
except Exception as e:
    print(f"❌ 未找到 MuMu: {e}")
    sys.exit(1)

# Test 3: MuMuManager
print("\n[3/5] 测试 MuMuManager...")
try:
    manager = MuMuManager()
    print(f"✅ MuMuManager 初始化成功")
    print(f"   管理器路径: {manager.manager_path}")
except Exception as e:
    print(f"❌ MuMuManager 失败: {e}")

# Test 4: Get players
print("\n[4/5] 测试获取玩家信息...")
try:
    players = manager.get_all_players_info()
    print(f"✅ 找到 {len(players)} 个玩家")
    for i, p in enumerate(players):
        if hasattr(p, 'index'):
            print(f"   玩家 {i}: {p.name} (index={p.index})")
except Exception as e:
    print(f"❌ 获取玩家失败: {e}")

# Test 5: MuMuApi
print("\n[5/5] 测试 MuMuApi...")
try:
    api = MuMuApi()
    dll = MuMuApi.get_mumu_dll_path()
    print(f"✅ MuMuApi 初始化成功")
    print(f"   DLL 路径: {dll}")
    print(f"   DLL 存在: {os.path.exists(dll)}")
except Exception as e:
    print(f"❌ MuMuApi 失败: {e}")

print("\n" + "=" * 60)
print("✅ 所有基础测试通过!")
print("=" * 60)
print("\n提示: 完整测试请运行 test_comprehensive.py")

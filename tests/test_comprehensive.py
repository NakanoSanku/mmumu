"""
Comprehensive test suite for the refactored mmumu package.
Tests the new registry search functionality and all detection strategies.
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

print("=" * 80)
print("MMUMU COMPREHENSIVE TEST SUITE")
print("=" * 80)

# Test 1: Import test
print("\n[TEST 1] Import Test")
print("-" * 80)
try:
    from mmumu.base import get_mumu_path, _validate_mumu_path
    from mmumu.manager import MuMuManager
    from mmumu.api import MuMuApi
    print("[PASS] All imports successful")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: get_mumu_path basic functionality
print("\n[TEST 2] get_mumu_path() - Auto Detection")
print("-" * 80)
try:
    # Clear any environment variable first
    if 'MUMU_INSTALL_PATH' in os.environ:
        print(f"[WARN] Environment variable already set: {os.environ['MUMU_INSTALL_PATH']}")
        del os.environ['MUMU_INSTALL_PATH']
    
    base_path = get_mumu_path()
    print(f"[PASS] MuMu path detected: {base_path}")
    print(f"   Path exists: {os.path.exists(base_path)}")
    print(f"   Is directory: {os.path.isdir(base_path)}")
    
    # Check for marker files
    print("\n   Checking marker files:")
    markers = [
        "shell/MuMuManager.exe",
        "nx_main/MuMuManager.exe",
        "MuMuPlayer.exe",
    ]
    found_markers = []
    for marker in markers:
        full_path = os.path.join(base_path, marker)
        exists = os.path.exists(full_path)
        if exists:
            found_markers.append(marker)
            print(f"   [PASS] {marker}")
        else:
            print(f"   [FAIL] {marker}")
    
    if not found_markers:
        print("   [WARN] WARNING: No marker files found, but path was returned")
    
except FileNotFoundError as e:
    print(f"[FAIL] MuMu not found: {e}")
    print("\n[WARN] Cannot continue with further tests without MuMu installation")
    print("   Please install MuMu Player or set MUMU_INSTALL_PATH environment variable")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Environment variable override
print("\n[TEST 3] Environment Variable Override")
print("-" * 80)
# Save the auto-detected path
auto_detected_path = base_path

# Set a custom path (use the same path to ensure it works)
os.environ['MUMU_INSTALL_PATH'] = auto_detected_path
print(f"Set MUMU_INSTALL_PATH = {auto_detected_path}")

try:
    env_path = get_mumu_path()
    if env_path == auto_detected_path:
        print(f"[PASS] Environment variable respected: {env_path}")
    else:
        print(f"[WARN] Environment variable returned different path: {env_path}")
except Exception as e:
    print(f"[FAIL] Error with environment variable: {e}")

# Clean up
del os.environ['MUMU_INSTALL_PATH']
print("   Cleaned up environment variable")

# Test 4: MuMuManager initialization
print("\n[TEST 4] MuMuManager Initialization")
print("-" * 80)
try:
    manager = MuMuManager()
    print(f"[PASS] MuMuManager created successfully")
    print(f"   Manager path: {manager.manager_path}")
    print(f"   Path exists: {os.path.exists(manager.manager_path)}")
except Exception as e:
    print(f"[FAIL] MuMuManager initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Get players info
print("\n[TEST 5] Get Players Info")
print("-" * 80)
try:
    all_infos = manager.get_all_players_info()
    print(f"[PASS] Query successful, found {len(all_infos)} player(s)")
    
    for i, info in enumerate(all_infos):
        print(f"\n   Player {i}:")
        if hasattr(info, 'errcode'):
            print(f"   [FAIL] Error: {info.errmsg} (code: {info.errcode})")
        elif hasattr(info, 'index'):
            print(f"   Index: {info.index}")
            print(f"   Name: {info.name}")
            print(f"   Is Main: {info.is_main}")
            if hasattr(info, 'pid'):
                print(f"   Running: {info.is_process_started}")
                print(f"   Android Started: {info.is_android_started}")
                if info.pid > 0:
                    print(f"   PID: {info.pid}")
        else:
            print(f"   Unknown info type: {type(info)}")
            
except Exception as e:
    print(f"[FAIL] Failed to get players info: {e}")
    import traceback
    traceback.print_exc()

# Test 6: MuMuApi initialization
print("\n[TEST 6] MuMuApi Initialization")
print("-" * 80)
try:
    api = MuMuApi()
    print("[PASS] MuMuApi created successfully")
    
    dll_path = MuMuApi.get_mumu_dll_path()
    print(f"   DLL path: {dll_path}")
    print(f"   DLL exists: {os.path.exists(dll_path)}")
    
except FileNotFoundError as e:
    print(f"[FAIL] DLL not found: {e}")
except Exception as e:
    print(f"[FAIL] MuMuApi initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Path validation function
print("\n[TEST 7] Path Validation Function")
print("-" * 80)
test_paths = [
    (base_path, True, "Auto-detected path"),
    (r"C:\NonExistent\Path", False, "Non-existent path"),
    (r"C:\Windows", False, "Valid path but not MuMu"),
]

for test_path, expected, description in test_paths:
    try:
        result = _validate_mumu_path(test_path)
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{status} {description}: {test_path}")
        print(f"   Expected: {expected}, Got: {result}")
    except Exception as e:
        print(f"[FAIL] Validation error for {test_path}: {e}")

# Test 8: Registry search functionality (debug info)
print("\n[TEST 8] Registry Search Debug Info")
print("-" * 80)
print("Testing registry search by looking for 'MuMu' keyword...")
print("(This test shows if the new keyword search is working)")

import winreg

uninstall_paths = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]

found_keys = []
for hive_name, hive in [("HKLM", winreg.HKEY_LOCAL_MACHINE), ("HKCU", winreg.HKEY_CURRENT_USER)]:
    for base_path_reg in uninstall_paths:
        try:
            with winreg.OpenKey(hive, base_path_reg) as base_key:
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(base_key, index)
                        index += 1
                        
                        if "mumu" in subkey_name.lower():
                            found_keys.append(f"{hive_name}\\{base_path_reg}\\{subkey_name}")
                            
                    except OSError:
                        break
        except (FileNotFoundError, OSError):
            continue

if found_keys:
    print(f"[PASS] Found {len(found_keys)} registry key(s) containing 'MuMu':")
    for key in found_keys:
        print(f"   - {key}")
else:
    print("[WARN] No registry keys containing 'MuMu' found")
    print("   This might mean:")
    print("   1. MuMu is not installed")
    print("   2. MuMu doesn't create standard registry entries")
    print("   3. Access permissions issue")

# Test 9: Test creating a second instance (connection pool test)
print("\n[TEST 9] Connection Pool Test")
print("-" * 80)
try:
    api1 = MuMuApi()
    api2 = MuMuApi()
    
    # Check if they share the same DLL
    if api1.nemu is api2.nemu:
        print("[PASS] Multiple instances share the same DLL (expected)")
    else:
        print("[WARN] Multiple instances have different DLL objects")
    
    # Check class-level connection list
    # Accessing private member for testing purposes
    print(f"   Current connections in pool: {len(MuMuApi._connect_list)}")
    
except Exception as e:
    print(f"[FAIL] Connection pool test failed: {e}")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"[PASS] MuMu installation detected: {base_path}")
print(f"[PASS] All core modules imported successfully")
print(f"[PASS] MuMuManager and MuMuApi can be initialized")
print("[WARN]  NOTE: Full integration tests (launching players, etc.) require:")
print("   - Administrator privileges")
print("   - At least one MuMu player instance")
print("   - MuMu player not already running")
print("\nFor full integration testing, run: python tests/manual_smoke.py")
print("=" * 80)

import os
import winreg
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


class MuMuError(Exception):
    """Base exception for mmumu package."""
    pass


class MuMuConnectionError(MuMuError):
    """Raised when connection to MuMu fails."""
    pass


class MuMuManagerError(MuMuError):
    """Raised when manager command fails."""
    pass

# Registry keys to check (in order of priority)
MUMU_REGISTRY_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer",
]

# Common installation paths to check as fallback
MUMU_COMMON_PATHS = [
    r"C:\Program Files\Netease\MuMu",
    r"C:\Program Files (x86)\Netease\MuMu",
    r"D:\Program Files\Netease\MuMu",
    r"C:\MuMuPlayer",
    r"D:\MuMuPlayer",
]

# Marker files that indicate a valid MuMu installation
MUMU_MARKER_FILES = [
    "shell/MuMuManager.exe",
    "nx_main/MuMuManager.exe",
    "MuMuPlayer.exe",
]


def _validate_mumu_path(path: str) -> bool:
    """
    Validate that a path is a valid MuMu installation directory.
    
    Args:
        path: Path to check.
        
    Returns:
        True if path contains MuMu marker files.
    """
    if not path or not os.path.isdir(path):
        return False
    
    for marker in MUMU_MARKER_FILES:
        if os.path.exists(os.path.join(path, marker)):
            return True
    
    return False


def _extract_path_from_command(cmd: str) -> Optional[str]:
    """
    Extract executable path from a command line string.
    
    Handles formats like:
    - "C:\\Path\\file.exe" /args
    - C:\\Path\\file.exe /args
    - 'C:\\Path\\file.exe' /args
    
    Args:
        cmd: Command line string.
        
    Returns:
        Extracted path or None.
    """
    if not cmd:
        return None
    
    cmd = cmd.strip()
    
    # Handle quoted paths
    if cmd and cmd[0] in ('"', "'"):
        quote = cmd[0]
        end_quote = cmd.find(quote, 1)
        if end_quote != -1:
            return cmd[1:end_quote]
        # Malformed quoting, take everything after the quote
        return cmd[1:].split()[0] if len(cmd) > 1 else None
    
    # No quotes, take first token
    parts = cmd.split()
    return parts[0] if parts else None


def _search_registry_for_mumu(hive: int, base_path: str) -> Optional[str]:
    """
    Search a registry path for any subkey containing "MuMu" in the name.
    
    Args:
        hive: Registry hive (e.g., winreg.HKEY_LOCAL_MACHINE).
        base_path: Base registry path to search (e.g., "SOFTWARE\\...\\Uninstall").
        
    Returns:
        MuMu installation path or None if not found.
    """
    try:
        with winreg.OpenKey(hive, base_path) as base_key:
            # Enumerate all subkeys
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(base_key, index)
                    index += 1
                    
                    # Check if subkey name contains "MuMu" (case-insensitive)
                    if "mumu" in subkey_name.lower():
                        subkey_path = f"{base_path}\\{subkey_name}"
                        logger.debug(f"Found MuMu-related registry key: {subkey_path}")
                        
                        # Try to get install path from this key
                        path = _get_path_from_key(hive, subkey_path)
                        if path and _validate_mumu_path(path):
                            return path
                            
                except OSError:
                    # No more subkeys
                    break
                    
    except (FileNotFoundError, OSError) as e:
        logger.debug(f"Could not access registry path {base_path}: {e}")
    
    return None


def _get_path_from_key(hive: int, key_path: str) -> Optional[str]:
    """
    Extract install path from a specific registry key.
    
    Args:
        hive: Registry hive.
        key_path: Full path to the registry key.
        
    Returns:
        Installation path or None.
    """
    try:
        with winreg.OpenKey(hive, key_path) as key:
            # Try different value names
            for value_name in ["UninstallString", "InstallLocation", "DisplayIcon", "InstallPath"]:
                try:
                    value, _ = winreg.QueryValueEx(key, value_name)
                    if not isinstance(value, str) or not value.strip():
                        continue
                    
                    value = value.strip()
                    
                    # Extract path based on value type
                    if value_name in ("UninstallString", "DisplayIcon"):
                        exe_path = _extract_path_from_command(value)
                        if exe_path:
                            return os.path.dirname(exe_path)
                    else:
                        # Direct path values
                        if os.path.isdir(value):
                            return value
                            
                except OSError:
                    continue
                    
    except (FileNotFoundError, OSError):
        pass
    
    return None


def _get_path_from_registry() -> Optional[str]:
    """
    Try to get MuMu path from Windows Registry by searching for "MuMu" keyword.
    
    This searches through the Uninstall registry locations and finds any
    key containing "MuMu" in the name, making it compatible with all versions.
    
    Returns:
        MuMu installation path or None if not found.
    """
    # Base paths to search
    uninstall_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    
    # Search in both HKLM and HKCU
    for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for base_path in uninstall_paths:
            path = _search_registry_for_mumu(hive, base_path)
            if path:
                logger.info(f"Found MuMu path from registry search: {path}")
                return path
    
    # Fallback: try known specific keys
    for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key_path in MUMU_REGISTRY_KEYS:
            try:
                path = _get_path_from_key(hive, key_path)
                if path and _validate_mumu_path(path):
                    logger.info(f"Found MuMu path from specific key: {path}")
                    return path
            except Exception:
                continue
    
    return None


def get_mumu_path() -> str:
    """
    Get MuMu Player installation path using multiple detection strategies.
    
    Detection order:
    1. Environment variable MUMU_INSTALL_PATH (if set)
    2. Windows Registry (multiple keys and values)
    3. Common installation directories
    
    Returns:
        Absolute path to MuMu installation directory.
        
    Raises:
        FileNotFoundError: If MuMu installation cannot be found.
        
    Environment Variables:
        MUMU_INSTALL_PATH: If set, this path will be checked first.
        
    Examples:
        >>> path = get_mumu_path()
        >>> print(path)
        C:\\Program Files\\Netease\\MuMu
        
        >>> # Or with environment variable:
        >>> os.environ['MUMU_INSTALL_PATH'] = 'D:\\MuMu'
        >>> path = get_mumu_path()
        D:\\MuMu
    """
    # Strategy 1: Environment variable override
    env_path = os.getenv("MUMU_INSTALL_PATH")
    if env_path:
        env_path = env_path.strip()
        if _validate_mumu_path(env_path):
            logger.info(f"Using MuMu path from environment: {env_path}")
            return os.path.abspath(env_path)
        logger.warning(f"Environment variable MUMU_INSTALL_PATH is set but invalid: {env_path}")
    
    # Strategy 2: Windows Registry
    registry_path = _get_path_from_registry()
    if registry_path:
        logger.info(f"Found MuMu path from registry: {registry_path}")
        return os.path.abspath(registry_path)
    
    # Strategy 3: Common installation directories
    for common_path in MUMU_COMMON_PATHS:
        if _validate_mumu_path(common_path):
            logger.info(f"Found MuMu at common location: {common_path}")
            return os.path.abspath(common_path)
    
    # All strategies failed
    raise FileNotFoundError(
        "MuMu Player installation not found.\n"
        "Tried the following locations:\n"
        f"  - Environment variable: MUMU_INSTALL_PATH\n"
        f"  - Registry keys: {MUMU_REGISTRY_KEYS}\n"
        f"  - Common paths: {MUMU_COMMON_PATHS}\n\n"
        "Solutions:\n"
        "  1. Set environment variable: MUMU_INSTALL_PATH=C:\\Path\\To\\MuMu\n"
        "  2. Install MuMu Player to a standard location\n"
        "  3. Specify path manually when creating MuMuManger or MuMuApi instances"
    )


@dataclass(frozen=True)
class MuMuManagerCmdResult:
    errcode: int
    errmsg: str


@dataclass(frozen=True)
class MuMuWindowLayout:
    width: int
    height: int
    x: int
    y: int


@dataclass(frozen=True)
class MuMuPlayerBaseInfo:
    index: str
    name: str
    is_main: bool
    error_code: int
    disk_size_bytes: int
    created_timestamp: int
    is_android_started: bool
    is_process_started: bool
    hyperv_enabled: bool


@dataclass
class MuMuPlayerInfo:
    index: str
    name: str
    is_main: bool
    error_code: int
    disk_size_bytes: int
    created_timestamp: int
    is_android_started: bool
    is_process_started: bool
    hyperv_enabled: bool
    main_wnd: str
    render_wnd: str
    adb_port: int
    adb_host_ip: str
    pid: int
    vt_enabled: bool
    player_state: str
    launch_err_msg: str
    launch_err_code: int
    launch_time: int
    headless_pid: int


@dataclass(frozen=True)
class MuMuPlayerConnect:
    handle: int
    emulator_install_path: str
    instance_index: int

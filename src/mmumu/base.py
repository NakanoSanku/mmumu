import os
import winreg
from dataclasses import dataclass

MUMU_UNINSTALL_KEY_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer"


def get_mumu_path() -> str:
    """
    Return the MuMu installation directory resolved from the Windows registry.

    The uninstall string is typically something like:
        "C:\\Program Files\\Netease\\MuMu\\uninstall.exe" /S

    This function extracts the executable path from the uninstall command
    and then returns its parent directory.

    Raises:
        FileNotFoundError: If the MuMu uninstall key does not exist.
        RuntimeError: If the uninstall entry cannot be read or parsed.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, MUMU_UNINSTALL_KEY_PATH
        ) as driver_key:
            uninstall_value = winreg.QueryValueEx(driver_key, "UninstallString")[0]
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"MuMuPlayer uninstall registry key '{MUMU_UNINSTALL_KEY_PATH}' not found"
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Failed to read MuMuPlayer uninstall entry: {exc}") from exc

    if not isinstance(uninstall_value, str) or not uninstall_value.strip():
        raise RuntimeError(
            f"Unexpected MuMuPlayer uninstall string value: {uninstall_value!r}"
        )

    cmd = uninstall_value.strip()

    # Extract the executable part from the uninstall command.
    if cmd[0] in ("'", '"'):
        quote = cmd[0]
        end = cmd.find(quote, 1)
        if end == -1:
            exe_part = cmd[1:]
        else:
            exe_part = cmd[1:end]
    else:
        # Take up to the first whitespace as the executable path.
        exe_part = cmd.split()[0]

    emulator_path = os.path.dirname(exe_part)
    if not emulator_path:
        raise RuntimeError(
            f"Could not determine MuMuPlayer install directory from uninstall string: {uninstall_value!r}"
        )

    return emulator_path


@dataclass(frozen=True)
class MuMuMangerCmdResult:
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

import winreg
from dataclasses import dataclass

MUMU_UNINSTALL_KEY_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer"


def get_mumu_path():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, MUMU_UNINSTALL_KEY_PATH) as driver_key:
            result = winreg.QueryValueEx(driver_key, "UninstallString")[0]
            emulator_path = result[1:result.index("\\uninstall.exe")]
            return emulator_path
    except FileNotFoundError:
        print(f"注册表键 '{MUMU_UNINSTALL_KEY_PATH}' 不存在")
    except Exception as e:
        print(f"发生错误: {e}")


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
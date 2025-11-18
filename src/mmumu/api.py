import os
import ctypes
from typing import List

from mmumu.base import MuMuPlayerConnect, get_mumu_path


class MuMuApi:
    nemu: ctypes.CDLL = None
    connect_list: List[MuMuPlayerConnect] = []

    def __init__(self, dll_path: str = None):
        """
        :param dll_path: path of mumu dll, if not set, will use default path.
        """
        if dll_path is None:
            dll_path = MuMuApi.get_mumu_dll_path()
        if MuMuApi.nemu is None:
            MuMuApi.nemu = ctypes.CDLL(dll_path)
            # 定义返回类型和参数类型
            self.nemu.nemu_connect.restype = ctypes.c_int
            self.nemu.nemu_connect.argtypes = [ctypes.c_wchar_p, ctypes.c_int]

            self.nemu.nemu_disconnect.argtypes = [ctypes.c_int]

            self.nemu.nemu_capture_display.restype = ctypes.c_int
            self.nemu.nemu_capture_display.argtypes = [
                ctypes.c_int,
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_ubyte),
            ]

            self.nemu.nemu_input_text.restype = ctypes.c_int
            self.nemu.nemu_input_text.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_char_p,
            ]

            self.nemu.nemu_input_event_touch_down.restype = ctypes.c_int
            self.nemu.nemu_input_event_touch_down.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
            ]

            self.nemu.nemu_input_event_touch_up.restype = ctypes.c_int
            self.nemu.nemu_input_event_touch_up.argtypes = [ctypes.c_int, ctypes.c_int]

            self.nemu.nemu_input_event_key_down.restype = ctypes.c_int
            self.nemu.nemu_input_event_key_down.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
            ]

            self.nemu.nemu_input_event_key_up.restype = ctypes.c_int
            self.nemu.nemu_input_event_key_up.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
            ]

    def connect(self, emulator_install_path: str, instance_index: int):
        for connect in self.connect_list:
            if (
                connect.emulator_install_path == emulator_install_path
                and connect.instance_index == instance_index
            ):
                return connect.handle
        res = self.nemu.nemu_connect(emulator_install_path, instance_index)
        if res == 0:
            raise Exception("connect error")
        self.connect_list.append(
            MuMuPlayerConnect(
                handle=res,
                emulator_install_path=emulator_install_path,
                instance_index=instance_index,
            )
        )
        return res

    def disconnect(self, handle: int):
        result = self.nemu.nemu_disconnect(handle)
        self.connect_list[:] = [c for c in self.connect_list if c.handle != handle]
        return result

    def get_display_id(self, handle: int, package_name: str, app_index: int):
        res = self.nemu.nemu_get_display_id(handle, package_name, app_index)
        if res < 0:
            raise Exception("get_display_id error")
        return res

    def capture_display(
        self,
        handle: int,
        display_id: int,
        buffer_size: int,
        width: ctypes.c_int,
        height: ctypes.c_int,
        pixels,
    ):
        res = self.nemu.nemu_capture_display(
            handle, display_id, buffer_size, width, height, pixels
        )
        if res > 0:
            raise Exception("capture_display error")
        return res

    def input_text(self, handle: int, size: int, buf: str):
        data = buf.encode("utf-8")
        if size <= 0:
            size = len(data)
        res = self.nemu.nemu_input_text(handle, size, data)
        if res > 0:
            raise Exception("input_text error")
        return res

    def input_event_touch_down(self, handle: int, display_id: int, x: int, y: int):
        res = self.nemu.nemu_input_event_touch_down(handle, display_id, x, y)
        if res > 0:
            raise Exception("input_event_touch_down error")
        return res

    def input_event_touch_up(self, handle: int, display_id: int):
        res = self.nemu.nemu_input_event_touch_up(handle, display_id)
        if res > 0:
            raise Exception("input_event_touch_up error")
        return res

    def input_event_key_down(self, handle: int, display_id: int, key_code: int):
        res = self.nemu.nemu_input_event_key_down(handle, display_id, key_code)
        if res > 0:
            raise Exception("input_event_key_down error")
        return res

    def input_event_key_up(self, handle: int, display_id: int, key_code: int):
        res = self.nemu.nemu_input_event_key_up(handle, display_id, key_code)
        if res > 0:
            raise Exception("input_event_key_up error")
        return res

    def input_event_finger_touch_down(
        self, handle: int, display_id: int, finger_id: int, x: int, y: int
    ):
        res = self.nemu.nemu_input_event_finger_touch_down(
            handle, display_id, finger_id, x, y
        )
        if res > 0:
            raise Exception("input_event_finger_touch_down error")
        return res

    def input_event_finger_touch_up(self, handle: int, display_id: int, slot_id: int):
        res = self.nemu.nemu_input_event_finger_touch_up(handle, display_id, slot_id)
        if res > 0:
            raise Exception("input_event_finger_touch_up error")
        return res

    @staticmethod
    def get_mumu_dll_path() -> str:
        base_path = get_mumu_path()
        candidates = [
            os.path.join(base_path, "shell", "sdk", "external_renderer_ipc.dll"),
            os.path.join(base_path, "nx_main", "sdk", "external_renderer_ipc.dll"),
        ]
        for dll_path in candidates:
            if os.path.exists(dll_path):
                return dll_path
        raise FileNotFoundError(
            "MuMu SDK DLL 'external_renderer_ipc.dll' not found in any of: "
            + ", ".join(candidates)
        )

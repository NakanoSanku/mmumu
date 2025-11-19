import os
import ctypes
import threading
from typing import List, ClassVar, Optional

from mmumu.base import MuMuPlayerConnect, get_mumu_path


class MuMuApi:
    """
    MuMu Player API wrapper using ctypes.
    
    Manages connections to the MuMu emulator backend DLL.
    Maintains a thread-safe global connection pool to avoid duplicate connections.
    """
    
    _nemu: ClassVar[Optional[ctypes.CDLL]] = None
    _connect_list: ClassVar[List[MuMuPlayerConnect]] = []
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, dll_path: str = None):
        """
        Initialize the MuMu API.
        
        Args:
            dll_path: Path to the MuMu DLL. If None, attempts to auto-detect.
        """
        if dll_path is None:
            dll_path = MuMuApi.get_mumu_dll_path()
            
        with self._lock:
            if MuMuApi._nemu is None:
                MuMuApi._nemu = ctypes.CDLL(dll_path)
                self._init_function_signatures()

    @property
    def nemu(self) -> ctypes.CDLL:
        """Get the underlying DLL instance."""
        if self._nemu is None:
            raise RuntimeError("MuMu API not initialized")
        return self._nemu

    def _init_function_signatures(self):
        """Initialize ctypes function signatures."""
        # Connection management
        self.nemu.nemu_connect.restype = ctypes.c_int
        self.nemu.nemu_connect.argtypes = [ctypes.c_wchar_p, ctypes.c_int]

        self.nemu.nemu_disconnect.argtypes = [ctypes.c_int]

        # Display capture
        self.nemu.nemu_capture_display.restype = ctypes.c_int
        self.nemu.nemu_capture_display.argtypes = [
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ubyte),
        ]

        self.nemu.nemu_get_display_id.restype = ctypes.c_int
        self.nemu.nemu_get_display_id.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int
        ]

        # Input events
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

        self.nemu.nemu_input_event_finger_touch_down.restype = ctypes.c_int
        self.nemu.nemu_input_event_finger_touch_down.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int
        ]

        self.nemu.nemu_input_event_finger_touch_up.restype = ctypes.c_int
        self.nemu.nemu_input_event_finger_touch_up.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int
        ]

    def connect(self, emulator_install_path: str, instance_index: int) -> int:
        """
        Connect to a MuMu instance.
        
        Args:
            emulator_install_path: Path to the emulator installation.
            instance_index: Index of the instance to connect to.
            
        Returns:
            Connection handle.
            
        Raises:
            Exception: If connection fails.
        """
        with self._lock:
            # Check existing connections
            for connect in self._connect_list:
                if (
                    connect.emulator_install_path == emulator_install_path
                    and connect.instance_index == instance_index
                ):
                    return connect.handle

            # Create new connection
            res = self.nemu.nemu_connect(emulator_install_path, instance_index)
            if res == 0:
                raise Exception("connect error")
            
            self._connect_list.append(
                MuMuPlayerConnect(
                    handle=res,
                    emulator_install_path=emulator_install_path,
                    instance_index=instance_index,
                )
            )
            return res

    def disconnect(self, handle: int) -> int:
        """
        Disconnect from a MuMu instance.
        
        Args:
            handle: Connection handle to disconnect.
            
        Returns:
            Result code from nemu_disconnect.
        """
        with self._lock:
            result = self.nemu.nemu_disconnect(handle)
            self._connect_list[:] = [c for c in self._connect_list if c.handle != handle]
            return result

    def close(self):
        """Disconnect all active connections."""
        with self._lock:
            for connect in list(self._connect_list):
                try:
                    self.nemu.nemu_disconnect(connect.handle)
                except Exception:
                    pass
            self._connect_list.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def get_display_id(self, handle: int, package_name: str, app_index: int) -> int:
        res = self.nemu.nemu_get_display_id(handle, package_name.encode('utf-8'), app_index)
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
    ) -> int:
        res = self.nemu.nemu_capture_display(
            handle, display_id, buffer_size, width, height, pixels
        )
        if res > 0:
            raise Exception("capture_display error")
        return res

    def input_text(self, handle: int, size: int, buf: str) -> int:
        data = buf.encode("utf-8")
        if size <= 0:
            size = len(data)
        res = self.nemu.nemu_input_text(handle, size, data)
        if res > 0:
            raise Exception("input_text error")
        return res

    def input_event_touch_down(self, handle: int, display_id: int, x: int, y: int) -> int:
        res = self.nemu.nemu_input_event_touch_down(handle, display_id, x, y)
        if res > 0:
            raise Exception("input_event_touch_down error")
        return res

    def input_event_touch_up(self, handle: int, display_id: int) -> int:
        res = self.nemu.nemu_input_event_touch_up(handle, display_id)
        if res > 0:
            raise Exception("input_event_touch_up error")
        return res

    def input_event_key_down(self, handle: int, display_id: int, key_code: int) -> int:
        res = self.nemu.nemu_input_event_key_down(handle, display_id, key_code)
        if res > 0:
            raise Exception("input_event_key_down error")
        return res

    def input_event_key_up(self, handle: int, display_id: int, key_code: int) -> int:
        res = self.nemu.nemu_input_event_key_up(handle, display_id, key_code)
        if res > 0:
            raise Exception("input_event_key_up error")
        return res

    def input_event_finger_touch_down(
        self, handle: int, display_id: int, finger_id: int, x: int, y: int
    ) -> int:
        res = self.nemu.nemu_input_event_finger_touch_down(
            handle, display_id, finger_id, x, y
        )
        if res > 0:
            raise Exception("input_event_finger_touch_down error")
        return res

    def input_event_finger_touch_up(self, handle: int, display_id: int, slot_id: int) -> int:
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

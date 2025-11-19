import json
import os
import subprocess
import logging
from typing import Union, List, Optional

from mmumu.base import (
    MuMuWindowLayout,
    MuMuManagerCmdResult,
    get_mumu_path,
    MuMuPlayerInfo,
    MuMuPlayerBaseInfo,
    MuMuManagerError,
)

logger = logging.getLogger(__name__)


class MuMuManager:
    """
    OVERVIEW: A utility for control mumu player.

    USAGE: <subcommand>

    OPTIONS:
      -h, --help                         Show help information.

    SUBCOMMANDS:
      info                               Get players info. [x]
      create                             Create players.[x]
      clone                              Clone players. (alias: copy)[x] 会卡住
      delete                             Delete players.[x]
      rename                             Rename players.[x] 会卡住
      import                             Import .mumudata files.
      export                             Export players as .mumudata files.
      control                            Control players.[x]
      setting                            Config players.
      adb                                Run adb cmd for players.[x]
      simulation                         Change simulated properties in players.[x]
      sort                               Layout player windows to sort.[x]
      driver                             Manage player drivers.[x]
      log                                Control manager log.[x]
    """

    def __init__(self, manager_path: str = None):
        if manager_path is None:
            manager_path = self.get_mumu_manager_path()
        self.manager_path = manager_path

    def get_player_info(self, player_index: int):
        cmd = ["info", "-v", f"{player_index}"]
        result = self.run_command_json(cmd)
        if "errcode" in result:
            return MuMuManagerCmdResult(result["errcode"], result["errmsg"])
        if "pid" in result:
            return MuMuPlayerInfo(**result)
        return MuMuPlayerBaseInfo(**result)

    def get_players_info(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["info", "-v", f"{player_index_list_str}"]
        result = self.run_command_json(cmd)
        # Normalize result to a list of info dicts
        if isinstance(result, dict):
            if "index" in result or "errcode" in result:
                infos = [result]
            else:
                infos = list(result.values())
        else:
            infos = result

        parsed: list[
            Union[MuMuPlayerBaseInfo, MuMuPlayerInfo, MuMuManagerCmdResult]
        ] = []
        for info in infos:
            if "errcode" in info and "index" not in info:
                parsed.append(MuMuManagerCmdResult(info["errcode"], info["errmsg"]))
            elif "pid" in info:
                parsed.append(MuMuPlayerInfo(**info))
            else:
                parsed.append(MuMuPlayerBaseInfo(**info))
        return parsed

    def get_all_players_info(self):
        cmd = ["info", "-v", "all"]
        result = self.run_command_json(cmd)
        if isinstance(result, dict):
            if "index" in result or "errcode" in result:
                infos = [result]
            else:
                infos = list(result.values())
        else:
            infos = result

        parsed: list[
            Union[MuMuPlayerBaseInfo, MuMuPlayerInfo, MuMuManagerCmdResult]
        ] = []
        for info in infos:
            if "errcode" in info and "index" not in info:
                parsed.append(MuMuManagerCmdResult(info["errcode"], info["errmsg"]))
            elif "pid" in info:
                parsed.append(MuMuPlayerInfo(**info))
            else:
                parsed.append(MuMuPlayerBaseInfo(**info))
        return parsed

    def create_player(self, player_index: int, number: int = None, mini: bool = False):
        cmd = ["create", "-v", f"{player_index}"]
        if number is not None:
            cmd.extend(["-n", str(number)])
        if mini:
            cmd.append("-m")
        return self.run_command_single_result(cmd)

    def create_players(self, player_index_list: list[int], number: int = None, mini: bool = False):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["create", "-v", f"{player_index_list_str}"]
        if number is not None:
            cmd.extend(["-n", str(number)])
        if mini:
            cmd.append("-m")
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    def create_all_players(self, number: int = None, mini: bool = False):
        cmd = ["create", "-v", "all"]
        if number is not None:
            cmd.extend(["-n", str(number)])
        if mini:
            cmd.append("-m")
        return self.run_command_multi_results(cmd)

    def delete_player(self, player_index: int):
        cmd = ["delete", "-v", f"{player_index}"]
        return self.run_command_single_result(cmd)

    def delete_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["delete", "-v", f"{player_index_list_str}"]
        return self.run_command_single_result(cmd)

    def delete_all_players(self):
        cmd = ["delete", "-v", "all"]
        return self.run_command_single_result(cmd)

    def launch_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "launch"]
        result_str = self.run_command(cmd)
        result = json.loads(result_str)
        return MuMuManagerCmdResult(result["errcode"], result["errmsg"])

    def launch_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "launch"]
        result_str = self.run_command(cmd)
        result = json.loads(result_str)
        if len(player_index_list) == 1:
            return MuMuManagerCmdResult(result["errcode"], result["errmsg"])
        return [MuMuManagerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]

    def launch_all_players(self):
        cmd = ["control", "-v", "all", "launch"]
        result_str = self.run_command(cmd)
        result = json.loads(result_str)
        return [MuMuManagerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]

    def shutdown_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "shutdown"]
        return self.run_command_single_result(cmd)

    def shutdown_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "shutdown"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    def restart_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "restart"]
        return self.run_command_single_result(cmd)

    def restart_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "restart"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    def restart_all_players(self):
        cmd = ["control", "-v", "all", "restart"]
        return self.run_command_multi_results(cmd)

    def show_window_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "show_window"]
        return self.run_command_single_result(cmd)

    def show_window_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "show_window"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)
    def show_window_all_players(self):
        cmd = ["control", "-v", "all", "show_window"]
        return self.run_command_multi_results(cmd)

    def hide_window_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "hide_window"]
        return self.run_command_single_result(cmd)

    def hide_window_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "hide_window"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    def hide_window_all_players(self):
        cmd = ["control", "-v", "all", "hide_window"]
        return self.run_command_multi_results(cmd)

    def get_player_window_layout_info(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "layout_window"]
        result = self.run_command_json(cmd)
        return MuMuWindowLayout(result["width"], result["height"], result["x"], result["y"])

    def get_players_window_layout_info(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "layout_window"]
        result = self.run_command_json(cmd)
        if len(player_index_list) == 1:
            return MuMuWindowLayout(result["width"], result["height"], result["x"], result["y"])
        return [MuMuWindowLayout(result[str(i)]["width"], result[str(i)]["height"], result[str(i)]["x"],
                                 result[str(i)]["y"]) for i in result]

    def create_player_shortcut(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "shortcut", "create"]
        return self.run_command_single_result(cmd)

    def create_players_shortcut(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "shortcut", "create"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    def create_all_players_shortcut(self):
        cmd = ["control", "-v", "all", "shortcut", "create"]
        return self.run_command_multi_results(cmd)

    def delete_player_shortcut(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "shortcut", "delete"]
        return self.run_command_single_result(cmd)

    def delete_players_shortcut(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "shortcut", "delete"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    def delete_all_players_shortcut(self):
        cmd = ["control", "-v", "all", "shortcut", "delete"]
        return self.run_command_multi_results(cmd)

    def sort(self):
        cmd = ["sort"]
        return self.run_command_single_result(cmd)

    def log(self, on: bool = True):
        cmd = ["log", "on" if on else "off"]
        return self.run_command_single_result(cmd)

    @staticmethod
    def get_mumu_manager_path() -> str:
        base_path = get_mumu_path()
        candidates = [
            os.path.join(base_path, "shell", "MuMuManager.exe"),
            os.path.join(base_path, "nx_main", "MuMuManager.exe"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        raise FileNotFoundError(
            "MuMuManager.exe not found in any of: " + ", ".join(candidates)
        )

    def run_command(self, command: list[str], timeout: int = 30) -> str:
        cmd = [self.manager_path]
        cmd.extend(command)
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                timeout=timeout
            )
            # Log warning if return code is non-zero, but don't raise exception yet as some commands might use it
            if result.returncode != 0:
                logger.warning(f"Command returned {result.returncode}: {cmd}")
                
            return result.stdout
            
        except subprocess.TimeoutExpired as exc:
            raise MuMuManagerError(f"Command timed out after {timeout}s: {command}") from exc
        except UnicodeDecodeError as exc:
            raise MuMuManagerError(f"Output decoding failed for command: {command}") from exc
        except Exception as exc:
            raise MuMuManagerError(f"Failed to execute command {command}: {exc}") from exc

    def run_command_json(self, command: list[str]):
        result_str = self.run_command(command)
        try:
            return json.loads(result_str)
        except json.JSONDecodeError as exc:
            raise MuMuManagerError(f"Failed to parse JSON output: {result_str}") from exc

    def run_command_single_result(self, command: list[str]):
        result = self.run_command_json(command)
        return MuMuManagerCmdResult(result["errcode"], result["errmsg"])

    def run_command_multi_results(self, command: list[str]):
        result = self.run_command_json(command)
        return [MuMuManagerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]

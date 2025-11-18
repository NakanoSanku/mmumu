import json
import os
import subprocess
from typing import Union

from mmumu.base import (
    MuMuWindowLayout,
    MuMuMangerCmdResult,
    get_mumu_path,
    MuMuPlayerInfo,
    MuMuPlayerBaseInfo,
)


class MuMuManger:
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

    def __init__(self, manger_path: str = None):
        if manger_path is None:
            manger_path = self.get_mumu_manger_path()
        self.manger_path = manger_path

    def get_player_info(self, player_index: int):
        cmd = ["info", "-v", f"{player_index}"]
        result = self.run_command_json(cmd)
        if "errcode" in result:
            return MuMuMangerCmdResult(result["errcode"], result["errmsg"])
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
            Union[MuMuPlayerBaseInfo, MuMuPlayerInfo, MuMuMangerCmdResult]
        ] = []
        for info in infos:
            if "errcode" in info and "index" not in info:
                parsed.append(MuMuMangerCmdResult(info["errcode"], info["errmsg"]))
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
            Union[MuMuPlayerBaseInfo, MuMuPlayerInfo, MuMuMangerCmdResult]
        ] = []
        for info in infos:
            if "errcode" in info and "index" not in info:
                parsed.append(MuMuMangerCmdResult(info["errcode"], info["errmsg"]))
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

    # def clone_player(self, player_index: int, number: int = None):
    #     cmd = ["clone", "-v", f"{player_index}"]
    #     if number is not None:
    #         cmd.extend(["-n", str(number)])
    #     return self.run_command(cmd)
    #
    # def clone_players(self, player_index_list: list[int], number: int = None):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["clone", "-v", f"{player_index_list_str}"]
    #     if number is not None:
    #         cmd.extend(["-n", str(number)])
    #     return self.run_command(cmd)
    #
    # def clone_all_players(self, number: int = None):
    #     cmd = ["clone", "-v", "all"]
    #     if number is not None:
    #         cmd.extend(["-n", str(number)])
    #     return self.run_command(cmd)

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

    # def rename_player(self, player_index: int, name: str):
    #     cmd = ["clone", "-v", f"{player_index}", "-n", name]
    #     result_str = self.run_command(cmd)
    #     result = json.loads(result_str)
    #     return [MuMuMangerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]
    #
    # def rename_players(self, player_index_list: list[int], name: int = None):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["clone", "-v", f"{player_index_list_str}", "-n", name]
    #     result_str = self.run_command(cmd)
    #     result = json.loads(result_str)
    #     return [MuMuMangerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]
    #
    # def rename_all_players(self, name: int = None):
    #     cmd = ["clone", "-v", "all", "-n", name]
    #     result_str = self.run_command(cmd)
    #     result = json.loads(result_str)
    #     return [MuMuMangerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]

    # def simulation_player_info(self, player_index: int, key: str, value: str):
    #     """
    #     修改模拟器信息
    #     :param player_index:
    #     :param key:
    #     1. android_id: Simulate Android ID properties.
    #     2. mac_address: Simulate MAC properties.
    #     3. imei: Simulate IMEI properties.
    #     :param value:
    #     1. __null__: set value to empty
    #     :return:
    #     """
    #     return self.run_command(["simulation", "-v", f"{player_index}", "-sk", key, "-sv", value])
    #
    # def simulation_players_info(self, player_index_list: list[int], key: str, value: str):
    #     """
    #     修改模拟器信息
    #     :param player_index_list:
    #     :param key:
    #     1. android_id: Simulate Android ID properties.
    #     2. mac_address: Simulate MAC properties.
    #     3. imei: Simulate IMEI properties.
    #     :param value:
    #     1. __null__: set value to empty
    #     :return:
    #     """
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     return self.run_command(["simulation", "-v", f"{player_index_list_str}", "-sk", key, "-sv", value])
    #
    # def simulation_all_players_info(self, key: str, value: str):
    #     """
    #     修改模拟器信息
    #     :param key:
    #     1. android_id: Simulate Android ID properties.
    #     2. mac_address: Simulate MAC properties.
    #     3. imei: Simulate IMEI properties.
    #     :param value:
    #     1. __null__: set value to empty
    #     :return:
    #     """
    #     return self.run_command(["simulation", "-v", "all", "-sk", key, "-sv", value])

    def launch_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "launch"]
        result_str = self.run_command(cmd)
        result = json.loads(result_str)
        return MuMuMangerCmdResult(result["errcode"], result["errmsg"])

    def launch_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "launch"]
        result_str = self.run_command(cmd)
        result = json.loads(result_str)
        if len(player_index_list) == 1:
            return MuMuMangerCmdResult(result["errcode"], result["errmsg"])
        return [MuMuMangerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]

    def launch_all_players(self):
        cmd = ["control", "-v", "all", "launch"]
        result_str = self.run_command(cmd)
        result = json.loads(result_str)
        return [MuMuMangerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]

    def shutdown_player(self, player_index: int):
        cmd = ["control", "-v", f"{player_index}", "shutdown"]
        return self.run_command_single_result(cmd)

    def shutdown_players(self, player_index_list: list[int]):
        player_index_list_str = ",".join(str(i) for i in player_index_list)
        cmd = ["control", "-v", f"{player_index_list_str}", "shutdown"]
        if len(player_index_list) == 1:
            return self.run_command_single_result(cmd)
        return self.run_command_multi_results(cmd)

    #TODO: 会卡住
    # def shutdown_all_players(self):
    #     cmd = ["control", "-v", "all", "shutdown"]
    #     return self.run_command_multi_results(cmd)

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

    # def get_all_players_window_layout_info(self):
    #     cmd = ["control", "-v", "all", "layout_window"]
    #     result_str = self.run_command(cmd)
    #     result = json.loads(result_str)
    #     return [MuMuWindowLayout(result[str(i)]["width"], result[str(i)]["height"], result[str(i)]["x"], result[str(i)]["y"]) for i in result]

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

    # def install_app_on_players(self, player_index_list: list[int], apk_path: str):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["control", "-v", f"{player_index_list_str}", "app", "install", "-apk", apk_path]
    #     if len(player_index_list) == 1:
    #         return self.run_command_single_result(cmd)
    #     return self.run_command_multi_results(cmd)
    # 
    # def install_app_on_all_players(self, apk_path: str):
    #     cmd = ["control", "-v", "all", "app", "install", "-apk", apk_path]
    #     return self.run_command_multi_results(cmd)
    # 
    # def uninstall_app_on_player(self, player_index: int, package_name: str):
    #     cmd = ["control", "-v", f"{player_index}", "app", "uninstall", "-pkg", package_name]
    #     return self.run_command_single_result(cmd)
    # 
    # def uninstall_app_on_players(self, player_index_list: list[int], package_name: str):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["control", "-v", f"{player_index_list_str}", "app", "uninstall", "-pkg", package_name]
    #     if len(player_index_list) == 1:
    #         return self.run_command_single_result(cmd)
    #     return self.run_command_multi_results(cmd)
    # 
    # def uninstall_app_on_all_players(self, package_name: str):
    #     cmd = ["control", "-v", "all", "app", "uninstall", "-pkg", package_name]
    #     return self.run_command_multi_results(cmd)
    # 
    # def launch_app_on_player(self, player_index: int, package_name: str):
    #     cmd = ["control", "-v", f"{player_index}", "app", "launch", "-pkg", package_name]
    #     return self.run_command_single_result(cmd)
    # 
    # def launch_app_on_players(self, player_index_list: list[int], package_name: str):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["control", "-v", f"{player_index_list_str}", "app", "launch", "-pkg", package_name]
    #     if len(player_index_list) == 1:
    #         return self.run_command_single_result(cmd)
    #     return self.run_command_multi_results(cmd)
    # 
    # def launch_app_on_all_players(self, package_name: str):
    #     cmd = ["control", "-v", "all", "app", "launch", "-pkg", package_name]
    #     return self.run_command_multi_results(cmd)
    # 
    # def close_app_on_player(self, player_index: int, package_name: str):
    #     cmd = ["control", "-v", f"{player_index}", "app", "close", "-pkg", package_name]
    #     return self.run_command_single_result(cmd)
    # 
    # def close_app_on_players(self, player_index_list: list[int], package_name: str):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["control", "-v", f"{player_index_list_str}", "app", "close", "-pkg", package_name]
    #     if len(player_index_list) == 1:
    #         return self.run_command_single_result(cmd)
    #     return self.run_command_multi_results(cmd)
    # 
    # def close_app_on_all_players(self, package_name: str):
    #     cmd = ["control", "-v", "all", "app", "close", "-pkg", package_name]
    #     return self.run_command_multi_results(cmd)
    # 
    # def get_app_state_on_player(self, player_index: int, package_name: str):
    #     cmd = ["control", "-v", f"{player_index}", "app", "info", "-pkg", package_name]
    #     return self.run_command_single_result(cmd)
    # 
    # def get_app_info_on_players(self, player_index_list: list[int], package_name: str):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["control", "-v", f"{player_index_list_str}", "app", "info", "-pkg", package_name]
    #     if len(player_index_list) == 1:
    #         return self.run_command_single_result(cmd)
    #     return self.run_command_multi_results(cmd)
    # 
    # def get_app_info_on_all_players(self, package_name: str):
    #     cmd = ["control", "-v", "all", "app", "info", "-pkg", package_name]
    #     return self.run_command_multi_results(cmd)
    # 
    # def list_app_info_on_player(self, player_index: int):
    #     cmd = ["control", "-v", f"{player_index}", "app", "info", "-i"]
    #     return self.run_command_single_result(cmd)
    # 
    # def list_app_info_on_players(self, player_index_list: list[int]):
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     cmd = ["control", "-v", f"{player_index_list_str}", "app", "info", "-i"]
    #     if len(player_index_list) == 1:
    #         return self.run_command_single_result(cmd)
    #     return self.run_command_multi_results(cmd)
    # 
    # def list_app_info_on_all_players(self):
    #     cmd = ["control", "-v", "all", "app", "info", "-i"]
    #     return self.run_command_multi_results(cmd)

    # def run_player_adb_sh(self, player_index: int, cmd: str):
    #     """
    #
    #     :param player_index:
    #     :param cmd:
    #     1. connect: Connect adb to player.
    #         == adb connect <host>:<ip>
    #     2. disconnect: Disconnect adb to player.
    #         == adb disconnect <host>:<ip>
    #     3. "getprop ro.opengles.version": Get android system props in player.
    #         == adb -s <host>:<ip> shell getprop ro.opengles.version
    #     4. "setprop ro.opengles.version xxx": Set android system props in player.
    #         == adb -s <host>:<ip> shell setprop ro.opengles.version xxx
    #     5. "input_text xxx": Input text to player.
    #         == adb -s <host>:<ip> shell input text xxx
    #     6. Input keyevent to player:
    #         go_back == adb -s <host>:<ip> shell input keyevent 4
    #         go_home == adb -s <host>:<ip> shell input keyevent 3
    #         go_task == adb -s <host>:<ip> shell input keyevent 187
    #         key_delete == adb -s <host>:<ip> shell input keyevent 67
    #         key_enter == adb -s <host>:<ip> shell input keyevent 66
    #         key_space == adb -s <host>:<ip> shell input keyevent 62
    #         volume_up == adb -s <host>:<ip> shell input keyevent 25
    #         volume_down == adb -s <host>:<ip> shell input keyevent 24
    #         volume_mute == adb -s <host>:<ip> shell input keyevent 164
    #     :return:
    #     """
    #     return self.run_command(["adb", "-v", f"{player_index}", "-c", cmd])

    # def run_players_adb_sh(self, player_index_list: list[int], cmd: str):
    #     """
    #
    #     :param player_index_list:
    #     :param cmd:
    #     1. connect: Connect adb to player.
    #         == adb connect <host>:<ip>
    #     2. disconnect: Disconnect adb to player.
    #         == adb disconnect <host>:<ip>
    #     3. "getprop ro.opengles.version": Get android system props in player.
    #         == adb -s <host>:<ip> shell getprop ro.opengles.version
    #     4. "setprop ro.opengles.version xxx": Set android system props in player.
    #         == adb -s <host>:<ip> shell setprop ro.opengles.version xxx
    #     5. "input_text xxx": Input text to player.
    #         == adb -s <host>:<ip> shell input text xxx
    #     6. Input keyevent to player:
    #         go_back == adb -s <host>:<ip> shell input keyevent 4
    #         go_home == adb -s <host>:<ip> shell input keyevent 3
    #         go_task == adb -s <host>:<ip> shell input keyevent 187
    #         key_delete == adb -s <host>:<ip> shell input keyevent 67
    #         key_enter == adb -s <host>:<ip> shell input keyevent 66
    #         key_space == adb -s <host>:<ip> shell input keyevent 62
    #         volume_up == adb -s <host>:<ip> shell input keyevent 25
    #         volume_down == adb -s <host>:<ip> shell input keyevent 24
    #         volume_mute == adb -s <host>:<ip> shell input keyevent 164
    #     :return:
    #     """
    #     player_index_list_str = ",".join(str(i) for i in player_index_list)
    #     return self.run_command(["adb", "-v", f"{player_index_list_str}", "-c", cmd])
    #
    # def run__all_players_adb_sh(self, cmd: str):
    #     """
    #
    #     :param cmd:
    #     1. connect: Connect adb to player.
    #         == adb connect <host>:<ip>
    #     2. disconnect: Disconnect adb to player.
    #         == adb disconnect <host>:<ip>
    #     3. "getprop ro.opengles.version": Get android system props in player.
    #         == adb -s <host>:<ip> shell getprop ro.opengles.version
    #     4. "setprop ro.opengles.version xxx": Set android system props in player.
    #         == adb -s <host>:<ip> shell setprop ro.opengles.version xxx
    #     5. "input_text xxx": Input text to player.
    #         == adb -s <host>:<ip> shell input text xxx
    #     6. Input keyevent to player:
    #         go_back == adb -s <host>:<ip> shell input keyevent 4
    #         go_home == adb -s <host>:<ip> shell input keyevent 3
    #         go_task == adb -s <host>:<ip> shell input keyevent 187
    #         key_delete == adb -s <host>:<ip> shell input keyevent 67
    #         key_enter == adb -s <host>:<ip> shell input keyevent 66
    #         key_space == adb -s <host>:<ip> shell input keyevent 62
    #         volume_up == adb -s <host>:<ip> shell input keyevent 25
    #         volume_down == adb -s <host>:<ip> shell input keyevent 24
    #         volume_mute == adb -s <host>:<ip> shell input keyevent 164
    #     :return:
    #     """
    #     return self.run_command(["adb", "-v", "all", "-c", cmd])

    def sort(self):
        cmd = ["sort"]
        return self.run_command_single_result(cmd)

    # # TODO:暂时不知道是什么驱动
    # def install_driver(self, name: str):
    #     return self.run_command(["driver", "install","-n",name])
    # def uninstall_driver(self, name: str):
    #     return self.run_command(["driver", "uninstall","-n",name])

    def log(self, on: bool = True):
        cmd = ["log", "on" if on else "off"]
        return self.run_command_single_result(cmd)

    @staticmethod
    def get_mumu_manger_path() -> str:
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

    def run_command(self, command: list[str]):
        cmd = [self.manger_path]
        cmd.extend(command)
        # 运行命令并获取输出
        result = subprocess.run(cmd, capture_output=True)
        return result.stdout.decode("utf-8")

    def run_command_json(self, command: list[str]):
        result_str = self.run_command(command)
        return json.loads(result_str)

    def run_command_single_result(self, command: list[str]):
        result = self.run_command_json(command)
        return MuMuMangerCmdResult(result["errcode"], result["errmsg"])

    def run_command_multi_results(self, command: list[str]):
        result = self.run_command_json(command)
        return [MuMuMangerCmdResult(result[str(i)]["errcode"], result[str(i)]["errmsg"]) for i in result]



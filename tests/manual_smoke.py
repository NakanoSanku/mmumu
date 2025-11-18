import time

from mmumu.base import get_mumu_path
from mmumu.manger import MuMuManger
from mmumu.api import MuMuApi


def main() -> None:
    print("== Base.get_mumu_path ==")
    base_path = get_mumu_path()
    print("MuMu base path:", base_path)

    print("\n== MuMuManger basic info ==")
    manger = MuMuManger()
    print("MuMuManager path:", manger.manger_path)

    all_infos = manger.get_all_players_info()
    print("All players info:", all_infos)
    if not all_infos:
        print("No players found; skipping player-specific tests.")
        return

    first = all_infos[0]
    if hasattr(first, "errcode"):
        print("First player info is an error:", first)
        return

    index = int(first.index)
    print(f"\nUsing player index: {index}")

    print("\n== Launch / shutdown player ==")
    launch_result = manger.launch_player(index)
    print("launch_player:", launch_result)

    # Give the emulator some time to start before SDK connect
    time.sleep(10)

    player_info = manger.get_player_info(index)
    print("get_player_info after launch:", player_info)

    print("\n== Sort and log toggle ==")
    try:
        sort_result = manger.sort()
        print("sort:", sort_result)
    except Exception as exc:  # noqa: BLE001
        print("sort error:", type(exc).__name__, exc)

    try:
        log_off = manger.log(on=False)
        print("log off:", log_off)
        log_on = manger.log(on=True)
        print("log on:", log_on)
    except Exception as exc:  # noqa: BLE001
        print("log toggle error:", type(exc).__name__, exc)

    print("\n== MuMuApi connect / disconnect ==")
    api = MuMuApi()
    dll_path = api.get_mumu_dll_path()
    print("DLL path:", dll_path)

    try:
        handle = api.connect(base_path, index)
    except Exception as exc:  # noqa: BLE001
        print("MuMuApi.connect error:", type(exc).__name__, exc)
    else:
        print("MuMuApi.connect handle:", handle)
        try:
            disconnect_res = api.disconnect(handle)
            print("MuMuApi.disconnect result:", disconnect_res)
        except Exception as exc:  # noqa: BLE001
            print("MuMuApi.disconnect error:", type(exc).__name__, exc)

    print("\n== Shutdown player ==")
    shutdown_result = manger.shutdown_player(index)
    print("shutdown_player:", shutdown_result)


if __name__ == "__main__":
    main()

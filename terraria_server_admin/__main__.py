from .config import Config
from .server_updater import get_latest_server
from .terraria_server import TerrariaServer
from pathlib import Path
import sys
import asyncio
from typing import Dict
from asyncio import sleep


async def ainput(*args):
    return await asyncio.to_thread(input, *args)


async def main():
    if len(sys.argv) > 1:
        conf = Config.from_json(Path(sys.argv[1]))
    else:
        conf = Config.from_json(Path('config.json'))
    latest_server = get_latest_server() / "Linux"
    servers: Dict[str, TerrariaServer] = {name: TerrariaServer(latest_server, c) for name, c in conf.servers.items()}
    for name, server in servers.items():
        print("starting server:", name)
        # server.print_output = True
        server.run()

    selected_server: TerrariaServer = next(iter(servers.items()))[1]
    selected_server.print_output = True
    while True:
        args = (await ainput()).strip().split()
        if not args:
            continue
        command = args.pop(0)
        if command == "exit_all":
            for _, server in servers.items():
                await server.stop()
            return
        elif command == "select" and len(args) >= 1:
            if args[0] in servers:
                if selected_server:
                    selected_server.print_output = False
                selected_server = servers[args[0]]
                selected_server.print_output = True
                print(f"Selected server: {args[0]}")
            else:
                print(f"Unknown server: {args[0]}")
        elif command == "list_servers":
            for server_name in servers:
                print("\t" + server_name)
        elif command == "regenerate" and selected_server:
            print(f"Are you sure you want to regenerate {selected_server.config.name}?")
            confirmation = (await ainput()).strip().lower()
            if confirmation not in ["yes", "y", "affirmative"]:
                continue
            await selected_server.stop()
            await selected_server.delete_world()
            selected_server.run()
        elif command == "restart" and selected_server:
            await selected_server.stop()
            await selected_server.run()
        elif command == "broadcast":
            if len(args) > 0:
                for name, server in servers.items():
                    await server.send_command("say", *args)
        elif selected_server:
            await selected_server.send_command(command, *args)


if __name__ == "__main__":
    asyncio.run(main())

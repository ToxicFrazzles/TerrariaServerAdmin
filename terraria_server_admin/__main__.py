from .config import Config
from .terraria_server import TerrariaServer
from .server_admin import ServerAdmin
from pathlib import Path
import sys


if len(sys.argv) > 1:
    config_path = Path(sys.argv[1])
else:
    config_path = Path('config.json')
admin: ServerAdmin = ServerAdmin(config_path)


@admin.command("exit_all")
async def exit_all(*args, server):
    for name, server in admin.servers.items():
        await server.stop()
    await admin.stop()


@admin.command("select")
async def select(server_name, *, server):
    if server_name in admin.servers:
        if admin.selected_server:
            admin.selected_server.print_output = False
        selected_server = admin.servers[server_name]
        selected_server.print_output = True
        print(f"Selected server: {server_name}")
    else:
        print(f"Unknown server: {server_name}")


@admin.command("list_servers")
async def list_servers(*, server):
    for server_name in admin.servers:
        print("\t" + server_name)


@admin.command("restart")
async def restart(*, server):
    await server.stop()
    server.run()


@admin.command("broadcast")
async def broadcast(*args, server):
    for name, server in admin.servers.items():
        await server.send_command("say", *args)


@admin.command("reload_config")
async def reload_config(*args, server):
    new_config = Config.from_json(config_path)
    updated_servers = admin.config.changed_servers(new_config)
    if not updated_servers:
        print("No config changes detected...")
        return
    for name in updated_servers:
        if name not in new_config.servers:
            # New config doesn't have a previously existing server. Time to stop it and remove
            server = admin.servers.pop(name)
            if server == admin.selected_server:
                admin.selected_server = None
            await server.stop()
        elif name not in admin.servers:
            # New config has a new server. Time to create it.
            admin.servers[name] = TerrariaServer(admin.latest_server, new_config.servers[name])
            admin.servers[name].run()
        else:
            # Existing server has been updated. Shut it down, swap the config and restart it.
            admin.servers[name].config = new_config.servers[name]
            await admin.servers[name].stop()
            admin.servers[name].run()
    admin.config = new_config
    print("Configs updated")


if __name__ == "__main__":
    # asyncio.run(main())
    admin.run()

import asyncio
from pathlib import Path
from typing import Optional, Dict
from .config import Config
from .terraria_server import TerrariaServer
from .server_updater import get_latest_server


async def ainput(*args):
    return await asyncio.to_thread(input, *args)


class ServerAdmin:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = Config.from_json(self.config_path)
        self.latest_server: Optional[Path] = None
        self.servers: Dict[str, TerrariaServer] = {}
        self.selected_server: Optional[TerrariaServer] = None
        self._command_handlers = {}
        self._running = False

    def command(self, cmd):
        def decorator(func):
            async def wrapper(*args):
                try:
                    await func(*args, server=self.selected_server)
                except Exception as e:
                    print(e)
            self._command_handlers[cmd] = wrapper
            return wrapper
        return decorator

    async def _command_event(self, command, *args):
        if command in self._command_handlers:
            await self._command_handlers[command](*args)
        elif self.selected_server:
            await self.selected_server.send_command(command, *args)

    async def _run(self):
        print("Checking for updates...")
        await self.update()
        print("Latest version of the Terraria server is installed")
        for name, config in self.config.servers.items():
            print("Starting server:", name)
            self.servers[name] = TerrariaServer(self.latest_server, config)
            self.servers[name].run()
            if self.selected_server is None:
                self.selected_server = self.servers[name]
                self.selected_server.print_output = True
        while self._running:
            args = (await ainput()).strip().split()
            if not args:
                continue
            command = args.pop(0)
            await self._command_event(command, *args)

    def run(self):
        self._running = True
        asyncio.run(self._run())

    async def update(self):
        self.latest_server = get_latest_server() / "Linux"

    async def stop(self):
        self._running = False


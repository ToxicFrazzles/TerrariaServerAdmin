import asyncio
from .config import ServerConfig
from pathlib import Path
from asyncio import sleep


class TerrariaServer:
    task: asyncio.Task
    p: asyncio.subprocess.Process

    def __init__(self, server_path: Path, config: ServerConfig):
        self.config = config
        self.print_output = False
        self.server_path = server_path

    async def _worker(self):
        command = " ".join([
            f'{self.server_path / "TerrariaServer.bin.x86_64"}',
            *self.config.command_arguments])
        self.p = await asyncio.create_subprocess_shell(
            command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )

        while self.p.returncode is None:
            if self.p.stdout.at_eof():
                break
            data = await self.p.stdout.readline()
            if self.print_output:
                print(f"[{self.config.name}]:", data.decode('utf-8').rstrip())

    def run(self):
        self.task = asyncio.create_task(self._worker())

    async def stop(self):
        await self.send_command("exit")
        try:
            await asyncio.wait_for(self.task, 120)
        except asyncio.TimeoutError:
            self.p.kill()
            self.task.cancel()
        self.p = None
        self.task = None

    async def send_command(self, command, *args):
        if self.p is None:
            return
        full_command = " ".join([command, *args]) + "\r\n"
        self.p.stdin.write(full_command.encode('utf-8'))
        await self.p.stdin.drain()

    async def delete_world(self):
        file_path = self.config.world
        file_path.unlink()

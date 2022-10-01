import json
from typing import Optional, Dict
from pathlib import Path


class Config:
    def __init__(self, *, servers, worldpath=None, **kwargs):
        self.worldpath = Path(worldpath or "~/.local/share/Terraria/Worlds")
        self.servers = {}
        for name, c in servers.items():
            for k, v in kwargs.items():
                c[k] = c.get(k, v)
            c['worldpath'] = c.get('worldpath', self.worldpath)
            self.servers[name] = ServerConfig(name=name, **c)

    @classmethod
    def from_json(cls, f):
        if isinstance(f, str):
            return Config(**json.loads(f))
        elif isinstance(f, Path):
            with f.open() as file:
                return Config(**json.load(file))
        else:
            return Config(**json.load(f))


class ServerConfig:
    def __init__(self, *, maxplayers=8, worldpath=None, name, seed=None, difficulty=0, autocreate=3, port, password=None):
        self.maxplayers = maxplayers
        self.worldpath = Path(worldpath or "~/.local/share/Terraria/Worlds")
        self.world = self.worldpath / f"name.replace(' ', '_').wld"
        self.worldpath.mkdir(exist_ok=True, parents=True)
        self.name = name
        self.seed = seed
        self.difficulty = difficulty
        self.autocreate = autocreate
        self.port = port
        self.password = password

    @property
    def command_arguments(self):
        args = [
            f"-maxplayers {self.maxplayers}",
            f"-worldpath {self.worldpath}",
            f"-world {self.world}",
            f"-worldname {self.name.replace(' ', '_')}",
            f"-port {self.port}",
            f"-difficulty {self.difficulty}",
            f"-autocreate {self.autocreate}"
        ]
        if self.password:
            args.append(f"-pass {self.password}")
        if self.seed:
            args.append(f"-seed {self.seed}")
        return args

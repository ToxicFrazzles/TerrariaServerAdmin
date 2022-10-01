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
    def __init__(self, *, maxplayers=8, worldpath=None, name, seed=None, difficulty=0, autocreate=3, port, password=None, regenerate_schedule=None, motd=None):
        self.maxplayers = maxplayers
        self.worldpath = Path(worldpath or "~/.local/share/Terraria/Worlds")
        self.world = self.worldpath / f"{name.replace(' ', '_')}.wld"
        self.worldpath.mkdir(exist_ok=True, parents=True)
        self.name = name
        self.seed = seed
        self.difficulty = difficulty
        self.autocreate = autocreate
        self.port = port
        self.password = password
        self.motd = motd

        self.regenerate_schedule = regenerate_schedule

    @property
    def config_file_contents(self):
        options = [
            f"world={self.world.resolve()}",
            f"autocreate={self.autocreate}",
            f"worldname={self.name}",
            f"difficulty={self.difficulty}",
            f"maxplayers={self.maxplayers}",
            f"port={self.port}",
            f"worldpath={self.worldpath.resolve()}"
        ]
        if self.seed:
            options.append(f"seed={self.seed}")
        if self.password:
            options.append(f"password={self.password}")
        if self.motd:
            options.append(f"motd={self.motd}")
        return "\r\n".join(options)

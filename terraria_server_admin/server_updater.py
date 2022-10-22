import re
import aiohttp
from pathlib import Path
from zipfile import ZipFile
from time import sleep


async def _get_json(url: str):
    async with aiohttp.ClientSession() as sesh:
        async with sesh.get(url) as r:
            r.raise_for_status()
            return await r.json()


async def get_latest_version_url():
    url = "https://terraria.org/api/get/dedicated-servers-names"
    name = (await _get_json(url))[0]
    return f"https://terraria.org/api/download/pc-dedicated-server/{name}"


async def _download_file(url, dest: Path):
    async with aiohttp.ClientSession() as sesh:
        async with sesh.get(url) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                async for data in r.content.iter_chunked(2**13):
                    f.write(data)


async def get_latest_server():
    url = await get_latest_version_url()
    version = re.findall(r'terraria-server-(\d+).*\.zip', url)[0]
    server = Path('server')
    if (server / version).is_dir():
        return server / version
    await _download_file(url, Path('server.zip'))
    with ZipFile(Path('server.zip'), 'r') as zip_ref:
        zip_ref.extractall(server)
    (server / version / "Linux" / "TerrariaServer.bin.x86_64").chmod(0o775)
    Path('server.zip').unlink()
    return server / version

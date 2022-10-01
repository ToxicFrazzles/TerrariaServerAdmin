import re
import requests
from pathlib import Path
from zipfile import ZipFile
from time import sleep


def get_latest_version_url():
    r = requests.get("https://terraria.org/api/get/dedicated-servers-names")
    r.raise_for_status()
    name = r.json()[0]
    return f"https://terraria.org/api/download/pc-dedicated-server/{name}"


def download_file(url, dest: Path):
    with dest.open("wb") as f, requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=2**13):
            f.write(chunk)


def get_latest_server():
    url = get_latest_version_url()
    version = re.findall(r'terraria-server-(\d+)\.zip', url)[0]
    server = Path('server')
    if (server / version).is_dir():
        return server / version
    download_file(url, Path('server.zip'))
    with ZipFile(Path('server.zip'), 'r') as zip_ref:
        zip_ref.extractall(server)
    (server / version / "Linux" / "TerrariaServer.bin.x86_64").chmod(0o775)
    Path('server.zip').unlink()
    return server / version

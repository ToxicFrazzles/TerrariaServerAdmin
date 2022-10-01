# TerrariaServerAdmin
A python program to manage Terraria servers

## Requirements

* Python 3.9+

## Usage

1. Clone this repository
2. Create a virtual environment
3. Activate the virtual environment
4. Create a config file using `example_config.json` as a template
5. Run the TerrariaServerAdmin tool using `python -m terraria_server_admin <path_to_config_file>`


## Commands

* `exit_all` gracefully closes all servers and the TerrariaServerAdmin program
* `list_servers` returns a list of all servers
* `select <server_name>` targets a server to receive commands
* `regenerate` shuts down the server, deletes the world file and restarts to generate a new world. It will prompt for confirmation before doing so.
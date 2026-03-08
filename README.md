# MCModUpdater (MCMU)

A utility to update and install Minecraft mods for java edition.

## Usage

```bash
$ mcmu
usage: MCModUpdater [-h] [-v] [-m MINECRAFT_DIR] [-g GAME_VERSION]
                    {update,remove,install} ...

positional arguments:
  {update,remove,install}

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -m, --minecraft_dir MINECRAFT_DIR
                        Path to the Minecraft folder, defaults to
                        '~/.minecraft/'
  -g, --game_version GAME_VERSION
                        Default game version

...
```

### Update installed mods

```bash
$ mcmu update -n
```

### Remove a mod

```bash
$ mcmu remove https://www.modrinth.com/mod/mod-name
```

### Install a mod

```bash
$ mcmu install https://www.modrinth.com/mod/mod-name
```

## FAQ

### Why did you build this?

I built this because I wanted to use Minecrafts default launcher but still be able to easily install and update mods like in Modrinths launcher.

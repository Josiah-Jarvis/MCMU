# MCModUpdater (MCMU)

A utility to update and install Minecraft mods for java edition. Only works for Fabric Loader.

## Usage

```bash
$ mcmu
usage: mcmu [-h] [-u] [-r REMOVE] [-i INSTALL] [-l] [-v] [-m MINECRAFT_DIR] [-g GAME_VERSION]

options:
  -h, --help            show this help message and exit
  -u, --update          Updates installed mods
  -r, --remove REMOVE   Removes an installed mod
  -i, --install INSTALL
                        Installs a mod
  -l, --list            List installed mods
  -v, --version         show program's version number and exit
  -m, --minecraft_dir MINECRAFT_DIR
                        Path to the Minecraft folder, defaults to '~/.minecraft/'
  -g, --game_version GAME_VERSION
                        Default game version
```

### Update installed mods

```bash
mcmu -u
```

### Remove a mod

```bash
mcmu -r mod-name
```

### Install a mod

```bash
mcmu -i mod-name
```

### List mods

```bash
mcmu -l
```

## FAQ

### Why did you build this?

I built this because I wanted to use Minecraft's default launcher but still be able to easily install and update mods like in Modrinth's launcher.

### Where do I get the mod name from?

Go to [Modrinth](https://modrinth.com) and search for you desired mod. Then get the part after the /mod/ in the url, that is the mod name.

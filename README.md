# MCModUpdater (MCMU)

A utility to update and install Minecraft mods for java edition. Only works for Fabric Loader (currently).

!IMPORTANT!

Your .minecraft/mods/ folder must be empty before you use this program. Unintended things might happen if it is not empty.

## Usage

```bash
$ mcmu --help
usage: mcmu [-h] [-u | -r REMOVE | -i INSTALL | -l | -s SEARCH | -d DEPENDENCY] [-m MINECRAFT_DIR] [-g GAME_VERSION]

A script to download mods from Modrinth

options:
  -h, --help            show this help message and exit
  -u, --update          Updates a mod (default: False)
  -r, --remove REMOVE   Remove a mod (default: None)
  -i, --install INSTALL
                        Install a mod (default: None)
  -l, --list            List mods (default: False)
  -s, --search SEARCH   Search mods on Modrinth (default: None)
  -d, --dependency DEPENDENCY
                        List a mods dependency's (default: None)
  -m, --minecraft_dir MINECRAFT_DIR
                        Path to the Minecraft folder (default: ~/.minecraft)
  -g, --game_version GAME_VERSION
                        The game version to use to install mods (default: 26.1)

Version: *2.0.1*

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

### Search mods

```bash
mcmu -s search_term
```

## Support

Supported operating systems are Debian and Fedora, it should work on Windows and MacOS to probably.

## FAQ

### Why did you build this?

I built this because I wanted to use Minecraft's default launcher but still be able to easily install and update mods like in Modrinth's launcher.

### Where do I get the mod name from?

Go to [Modrinth](https://modrinth.com) and search for you desired mod. Then get the part after the /mod/ in the url, that is the mod name.

### Why can't I downgrade mods?

As of now you can not downgrade most mods because the installer always checks for the latest version. For example if you have a mod that releases version 12 for Minecraft 1.21.11 but its latest version for Minecraft 1.21.10 is 11 then you can not downgrade that mod.

A solution!

Do:

```bash
mcmu -r mod-name
mcmu -g game_version -i mod-name
```

### How does it work?

It works a lot like a package manager actually! It pulls the mods from a source (Modrinth) and installs them on the system. It keeps a list of the installed mods in a config file for easy access of the installed mods.

### What happened to v1.4.0?

It turned into v2.0.0.

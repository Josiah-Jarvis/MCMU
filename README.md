# MCModUpdater (MCMU)

A utility to update and install Minecraft mods for java edition. Only works for Fabric Loader (currently).

!IMPORTANT!

Your .minecraft/mods/ folder must be empty before you use this program. Unintended things might happen if it is not empty.

## Usage

```bash
$ mcmu --help
usage: mcmu [-h] [--mod-dir MOD_DIR] [--game-version GAME_VERSION] [--verbose] [-v] {update,remove,install,list,search,info,enable,disable,backup} ...

A script to download mods from Modrinth

options:
  -h, --help            show this help message and exit
  --mod-dir MOD_DIR     Path to the Minecraft mods folder (default: /home/josiahjarvis/.minecraft/mods)
  --game-version GAME_VERSION
                        The game version to use to install mods (default: 26.1.2)
  --verbose             Increase logging level (default: False)
  -v, --version         Display the version

subcommands:
  The function to run

  {update,remove,install,list,search,info,enable,disable,backup}
                        Action to run
    update              Update mods
    remove              Remove a mod
    install             Install a mod
    list                List mods
    search              Search mods
    info                Get info on a mod
    enable              Enable a mod
    disable             Disable a mod
    backup              Backup mods folder

Version: 2.2.0
```

## Support

Supported operating systems are Linux, MacOS, and Windows.

## FAQ

### Why did you build this?

I built this because I wanted to use Minecraft's default launcher but still be able to easily install and update mods like in Modrinth's launcher.

### Where do I get the mod name from?

Go to [Modrinth](https://modrinth.com) and search for you desired mod. Then get the part after the /mod/ in the url, that is the mod name.

### How does it work?

It works a lot like a package manager actually! It pulls the mods from a source (Modrinth) and installs them on the system.
# MCModUpdater (MCMU)

A utility to update and install Minecraft mods for java edition. Only works for Fabric Loader (currently).

**!IMPORTANT!**

Your .minecraft/mods/ folder must be empty before you use this program. Unintended things might happen if it is not empty.

## Usage

```bash
$ mcmu --help
usage: mcmu [-h] [-v] [--verbose] [-l {fabric,forge,neoforge,babric,quilt,bukkit,folia,paper,purpur,spigot,sponge}] [-c {release,beta,alpha}] [--mod-dir MOD_DIR] [--game-version GAME_VERSION]
            {update,remove,install,list,search,info,enable,disable} ...

A robust package to install, update, and manage Minecraft mods

options:
  -h, --help            show this help message and exit
  -v, --version         Display the version
  --verbose             Increase logging level
  -l, --loader {fabric,forge,neoforge,babric,quilt,bukkit,folia,paper,purpur,spigot,sponge}
                        The mod loader to target for
  -c, --channel {release,beta,alpha}
                        The channel to get mods from
  --mod-dir MOD_DIR     Path to the Minecraft mods folder
  --game-version GAME_VERSION
                        The game version to use to install mods

subcommands:
  The function to run

  {update,remove,install,list,search,info,enable,disable}
    update              Update mods
    remove              Remove a mod
    install             Install a mod
    list                List mods
    search              Search mods
    info                Get info on a mod
    enable              Enable a mod
    disable             Disable a mod

Try 'mcmu COMMAND --help'
```

## Support

Supported operating systems are Linux, MacOS, and Windows.

## FAQ

### Why did you build this?

I built this because I wanted to use Minecraft's default launcher but still be able to easily install and update mods like in Modrinth's launcher.

### Where do I get the mod name from?

Go to [Modrinth](https://modrinth.com) and search for you desired mod. Then get the part after the /mod/ in the url, that is the mod name to use (don't include the last forward slash).

### How does it work?

It works a lot like a package manager actually! It pulls the mods from a source (Modrinth) and installs them on the system.
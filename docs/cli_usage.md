# Command line usage of MCMU

This is a guide on how to use MCMU!

## Options

MCMU has several options that may be used.

### mcmu -h/--help

Using the -h/--help option will print the help message.

### mcmu -v/--version

Using the -v/--version option will print the version of MCMU.

### mcmu --mod-dir <mod-dir>

Specifies the path to the mod-dir.

## Commands

MCMU has several command line commands that specifiy what you want the program to do.

### mcmu update

Running `mcmu update` try's to update all installed mods.

Update has several options.

#### mcmu update --channel {release,beta,alpha}

This option specifes the release channel to update from.

#### mcmu update --loader <loader>

This option specifies the loader to update for. Run `mcmu update -h` to get a complete list.

#### mcmu update --game-version <game-version>

This option specifies the game version to update for. Run `mcmu update -h` to get a complete list.

### mcmu remove <mod>

Remove, removes the specified mod.

### mcmu install <mod>

Running `mcmu install <mod>` installes the specified mod. If you run `mcmu install <mod==version>` it will install the specified version if it exists.

Install has several options.

#### mcmu install <mod> --channel {release,beta,alpha}

This option specifes the release channel to install from.

#### mcmu install <mod> --loader <loader>

This option specifies the loader to install for. Run `mcmu install -h` to get a complete list.

#### mcmu install <mod> --game-version <game-version>

This option specifies the game version to install for. Run `mcmu install -h` to get a complete list.


### mcmu list

Running `mcmu list` lists all installed mods.

#### mcmu list --enabled

Using the --enabled flag only lists mods that are enabled

#### mcmu list --disabled

Using the --disabled flag only lists mods that are disabled

### mcmu search <term>

Running `mcmu search <term>` searchs Modrinth for the specified term.

#### mcmu search <term> --offset

Using --offset offsets the results by the specified amount.

#### mcmu search <term> --sorting

Using --sorting changes the sorting method. Run `mcmu search -h` to get a complete list of sorting methods.

#### mcmu search <term> --category

Using --category filters by category. Run `mcmu search -h` to get a complete list of category's methods.

#### mcmu search <term> --limit

Using --limit limits the number of search results, must be between 1 and 100.

#### mcmu search <term> --versions

Using this option adds a version to filter for. You can use this option multiple times. Run `mcmu search -h` to get a complete a list.

#### mcmu search <term> --server-side {required,optional,unsupported,unknown}

Filters by server side support.

#### mcmu search <term> --client-side {required,optional,unsupported,unknown}

Filters by client side support.

#### mcmu search <term> --open-source

Filters by open source support.

#### mcmu seaerch <term> --loader

Filters by loader. Run `mcmu search -h` to get a complete list.

### mcmu info <mod>

Get info on the specified mod.

### mcmu enable <mod>

Enables the specified mod.

### mcmu disable <mod>

Disables the sepcified mod. Disabled mods are stored as .jar.disabled files.

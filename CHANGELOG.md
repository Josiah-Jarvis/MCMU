# Changelog

## [1.3.0a1] - 2026-03-15

### Removed

* Removed print statement for parameters

## [1.3.0a0] - 2026-03-15

This release brings a new feature! You can now search mods on Modrinth!

### Added

* Functionality to search mods

### Fixed

* Fixed passing parameters for installing mods

### Changed

* Does'nt ask to download mod if it is already installed
* Now most command lines options are mutually exclusive

## [1.2.1] - 2026-03-13

### Changed

* Change help message for the -g command line argument

## [1.2.0] - 2026-03-13

Happy Pi days for reals this time

No changes from [1.2.0rc0](#120rc0---2026-03-13)

## [1.2.0rc0] - 2026-03-13

If no serious bugs are found this release will become [1.2.0](#120---2026-03-13)

### Fixed

* Fixed mod failing to update because of "AttributeError: 'PosixPath' object has no attribute 'stats'. Did you mean: 'stat'?"
* Fixed when updating mods a new mod entry is made titled null breaking future update runs

### Changed

* Took check_update() code out of Mod class

### Removed

* Removed Mod class

## [1.2.0a1] - 2026-03-13

### Changed

* Now shows additional storage that will be taken up by updating a mod
* Now uses Mod.check_update() instead of Mod.install() when installing a mod

### Removed

* Removed Mod.install()

## [1.2.0a0] - 2026-03-13

### Added

* Shows space that will be taken up by a new mod
* Shows space that will be saved when removing a mod

### Changed

* Now asks for permission to install mod
* Now asks for permission to remove mod
* Moved *minecraft_mod.py* code into *__main__.py*

## [1.2.0.dev1] - 2026-03-13

### Added

* Added a message when a mod is removed

## [1.2.0.dev0] - 2026-03-13

### Changed

* Made update messages pretty

## [1.1.1] - 2026-03-13

Happy almost Pi Day! Here is the newest stable release.

### Changed

- Changed sys.exit() to return statements.

## [1.1.1a0] - 2026-03-12

1.1.1 is scheduled for 14 March 2026 (Pi day)

### Changed

- Changed default version for Minecraft to 26.1 for the soon to be released 26.1
- Made version message pretty
- Took deleting mod files out of *minecraft_mod.py* and put it in *__main__.py*

### Security

- Changed python required version to >=3.13 to reflect the supported python versions: [Status of Python versions](https://devguide.python.org/versions/)

## [1.1.0] - 2026-03-12

### Fixed

- Fixed "NameError: name 'Path' is not defined" when trying to delete a mod

## [1.1.0.dev1] - 2026-03-11

### Changed

- Future support for other mod loaders removed

### Removed

- Removed duplicate code in src/mcmu/minecraft_mod.py

## [1.1.0.dev0] - 2026-03-10

### Added

- You can list installed mods now

### Changed

- Started implemented a logging system

## [1.0.0] - 2026-03-10

First stable release.

## [1.0.0rc1] - 2026-03-10

### Changed

- Now only needs mods name not mods URL to install

### Fixed

- Fixed not creating the config file on start

## [1.0.0rc0] - 2026-03-10

This is the first release candidate for version [1.0.0+1.21.11].

### Changed

- Dedicated functions for loading and writing config file

### Fixed

- Fixed "NameError: name 'requests' is not defined" when trying to install a mod

## [0.2.2] - 2026-03-08

### Added

- Added help messages to command line arguments

### Changed

- When no options are present prints help message

## [0.2.1] - 2026-03-07

- Dummy Release

## [0.2.0] - 2026-03-07

### Changed

- Changed name from "MCModUpdater" to "mcm"
- Changed command line arguments around

## [0.1.4] - 2026-03-06

### Fixed

- Fixed Downloading latest mod version instead of latest version for the current installed Minecraft version

### Changed

- Removed some of the debug print statements

## [0.1.3] - 2026-03-06

### Added

- Checks for mod updates

## [0.1.2] - 2026-03-06

### Added

- Now can download and install mods
- Can delete mods

### Fixed

- Script executing twice

## [0.1.1] - 2026-03-06

### Added

- Check Modrinth for mod versions
- Get list of mods from config file
- Add mods to config file

## [0.1.0] - 2026-03-03

- Initial Release

[0.1.0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.1.0
[0.1.1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.1.1
[0.1.2]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.1.2
[0.1.3]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.1.3
[0.1.4]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.1.4
[0.2.0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.2.0
[0.2.1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.2.1
[0.2.2]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/0.2.2
[1.0.0rc0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.0.0rc0
[1.0.0rc1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.0.0rc1
[1.0.0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.0.0
[1.1.0.dev0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.1.0.dev0
[1.1.0.dev1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.1.0.dev1
[1.1.0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.1.0
[1.1.1a0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.1.1a0
[1.1.1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.1.1
[1.2.0.dev0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.0.dev0
[1.2.0.dev1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.0.dev1
[1.2.0a0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.0a0
[1.2.0a1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.0a1
[1.2.0rc0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.0rc0
[1.2.0]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.0
[1.2.1]: https://github.com/Josiah-Jarvis/MCModUpdater/releases/tag/1.2.1

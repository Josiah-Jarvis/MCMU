# Config.json reference

This files contains documentation for the config.json file that contains configuration options.

## Structure

Here is the structure for the file:

```json
{
    "mods": {
        "mod0_name": {
            "file": "mods_jar_file.jar",
            "version": "Mod Version",
            "name": "Name of the mods version"
        },
        "mod1_name": {
            "file": "mods_jar_file.jar",
            "version": "Mod Version",
            "name": "Name of the mods version"
        }
    }
}
```

## mods

The mods key is a dictionary of all the installed mods.

### Mod element structure

The key is the name of the mod. The value is a dictionary with 3 items [file, version, name].

"file" and "version" are mandatory but "name" is not.

"file" is the name of the .jar file as stored in the mods/ directory.

"version" is the mods current version as installed.

"name" is the name of the mods current version as installed.

# Breaking changes between v1.3.0 and v2.0.0

This update breaks everything!

Why does it break everything? Because we are dropping the config file! Now the config is stored in the mods file name, now it is stored as {mod_name}_version_{mod_version}.jar.

## How to update safely

In v1.3.0 of MCMU do `mcmu -l` to get a list of all your mods. Keep this safe. One by one delete all your mods with `mcmu -r <modname>` then update MCMU with `pip install --upgrade mcmu`. Next reinstall all your mods with `mcmu -i <modname>`.

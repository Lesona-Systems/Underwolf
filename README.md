# Underwolf

Underwolf is a Python script to update World of Warcraft addons without the need for any third-party addon managers. It's capable of version-checking and downloading Curseforge addons and ElvUI, as well as bulk downloading any other addons with direct download links.

**Pull & feature requests are welcome. Please report any issues you encounter.**

Underwolf utilizes Python's built-in webbrowser library to navigate to either legacy [CurseForge](https://legacy.curseforge.com/) download pages, the new Curseforge website, and any other addons that provide direct download URLs, such as [Tukui](https://legacy.tukui.org) and [Trade Skill Master](https://legacy.tradeskillmaster.com/) and download the specified addons, unzip them, and move them into the WoW addon folder. The script utilizes Selenium for version checking (version checking is only implemented on CurseForge addons and TukUI/ElvUI).

### Skip Version Checking

You can alternatively run `main.py` with the `--forceupdate` flag to skip version checking and force download every addon in addon_master_list.json (useful for initial installs of WoW as well as patch days, where several versions of an addon can be released on the same day).

**The script works on MacOS, Windows, and Linux (tested with Lutris, but should work with whichever Linux launcher you use).**


## Requirements

### Clone Underwolf

Clone the repo, cd into the directory, and run the following:

    python3 -m venv venv

then activate the virtual environment and run

    pip install -r requirements.txt

### Provide required paths in config.ini

#### Download Directory

If you have a custom download directory set for Firefox, add the full path of your Firefox download directory to `config.ini`. For example:

    firefox_download_directory = C:\Users\username\{CustomDir}

If you are using your OS' default download directory, leave this field blank.

#### World of Warcraft Addon Directory

Add the full path of your World of Warcraft Addon directory to `config.ini`. For example:

    wow_addon_directory = C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns

#### Ublock Origin

The script currently **requires [Firefox](https://www.mozilla.org/en-US/firefox/new/) and [uBlock Origin](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/).** uBlock Origin "fast-forwards" the CurseForge imposed 5-second wait time (as well as other sites) before the download starts on the download pages. Additionally, it cuts the total amount of time for the script to execute by around half.

In order to use uBlock Origin with Underwolf, you have to provide the system path to uBlock's `.xpi` file in `config.ini`. For example:

    ublock_xpi_path = C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\RANDOMSTRING.default-release\extensions\uBlock0@raymondhill.net.xpi

On Windows, you can find Mozilla's extension folder here with a default installation:

    C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\RANDOMSTRING.default-release\extensions\uBlock0@raymondhill.net.xpi

On Mac:

    /Users/username/Library/Application Support/Firefox/Profiles/RANDOMSTRING.default-release/extensions/uBlock0@raymondhill.net.xpi

On Linux:

    /home/username/.mozilla/firefox/RANDOMSTRING.default-release/extensions/uBlock0@raymondhill.net.xpi

`config.ini` is currently populated with an example path. You **must** provide a valid path to the `.xpi` file for the script to successfully execute.

**The script will not work without uBlock Origin.**

### Install the geckodriver

The script uses Selenium and built-in Python libraries - you must have the [Firefox Gecko driver](https://github.com/mozilla/geckodriver/releases) appropriate for your system. Unzip the driver into the Underwolf directory on MacOS and Windows. 

In Linux, move the geckodriver you've downloaded to:

    /usr/local/bin

Note that the script calls **taskkill** on all Firefox processes at the end to clean up.

### Add addons to addons_master_list.json

#### Adding Curseforge Addons
Curseforge addons can use either a `legacy.curseforge.com` or `curseforge.com` URL for its anchor_link. Please note that if you choose to use the ***non-legacy Curseforge URL***, you will only be able to update the addon once per day without resorting to the `--forceupdate` flag. See [#24](https://github.com/Lesona-Systems/Underwolf/issues/24) for more information.
Add Curseforge addons to `addon_master_list.json` like so:

    "DBM" : {
        "location" : "cf",
        "anchor_link" : "https://legacy.curseforge.com/wow/addons/deadly-boss-mods",
        "dl_url" : "https://curseforge.com/wow/addons/deadly-boss-mods/download",
        "last_updated" : ""
    },

Underwolf is currently using the legacy Curseforge website for version tracking since it gives the Unix epoch that the addon was updated. The new CF website only specifies if the addon has been updated that day.

#### Adding ElvUI 
Copy the following and add it to your `addons_master_list.json` and the script will take care of the rest.

    "ELVUI" : {
        "location" : "elvui",
        "anchor_link" : "https://www.tukui.org/elvui",
        "dl_url" : "https://www.tukui.org/elvui",
        "current_version" : ""
    }

#### Adding TukUI
Copy the following and add it to your `addons_master_list.json` and the script will take care of the rest.

    "TUKUI" : {
        "location" : "tukui",
        "anchor_link" : "https://www.tukui.org/tukui",
        "dl_url" : "https://tukui.org/tukui",
        "current_version" : ""
    }

The script will also backup `master_addon_list.json` at the beginning of each run.

Tested on MacOS, Windows, and Debian with **uBlockOrigin 1.44.4**. Tested on Python 3.10.6, but should work with Python 3.+.

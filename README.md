# Underwolf

Underwolf is a Python script to update World of Warcraft addons without the need for any third-party addon managers. It's capable of version-checking and downloading Curseforge addons and ElvUI, as well as bulk downloading any other addons with direct download links.
**This software is still in pre-release, and there may be bugs. Pull & feature requests are welcome. Please report any issues you encounter.**

Underwolf utilizes Python's built-in webbrowser library to navigate to [CurseForge](https://www.curseforge.com/) download pages (as well as other direct download URLs, such as [Tukui](https://www.tukui.org) and [Trade Skill Master](https://www.tradeskillmaster.com/)) and download the specified addons, unzip them, and move them into the WoW addon folder. The script utilizes Selenium for version checking (version checking is only implemented on CurseForge addons and ElvUI).

The script works on both MacOS and Windows. It's slow, but if you don't want to touch the CF app or its web interface, it'll work just fine.

## Requirements

### Clone Underwolf

Clone the repo, cd into the directory, and run the following:

    python3 -m venv venv

then activate the virtual environment and run

    pip install -r requirements.txt

### Provide required paths in config.ini

#### Download Directory

Add the full path of your Firefox download directory to config.ini. For example:

    firefox_download_directory = C:\Users\username\Downloads

#### World of Warcraft Addon Directory

Add the full path of your World of Warcraft Addon directory to config.ini. For example:

    wow_addon_directory = C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns

#### Ublock Origin

The script currently **requires [Firefox](https://www.mozilla.org/en-US/firefox/new/) and [uBlock Origin](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/).** uBlock Origin "fast-forwards" the CurseForge imposed 5-second wait time (as well as other sites) before the download starts on the download pages. Additionally, it cuts the total amount of time for the script to execute by around half.

In order to use uBlock Origin with Underwolf, you have to provide the system path to uBlock's .xpi file in config.ini. For example:

    ublock_xpi_path = C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\RANDOMSTRING.default-release\extensions\uBlock0@raymondhill.net.xpi

On Windows, you can find Mozilla's extension folder here with a default installation:

    C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\RANDOMSTRING.default-release\extensions\uBlock0@raymondhill.net.xpi

On Mac:

    /Users/username/Library/Application Support/Firefox/Profiles/RANDOMSTRING.default-release/extensions/uBlock0@raymondhill.net.xpi

config.ini is currently populated with an example path. You **must** provide a valid path to the .xpi file for the script to successfully execute.

**The script will not work without uBlock Origin.**

### Install the geckodriver

The script uses Selenium and built-in Python libraries - you must have the [Firefox Gecko driver](https://github.com/mozilla/geckodriver/releases) appropriate for your system. Unzip the driver into the Underwolf directory.

Note that the script calls **taskkill** on all Firefox processes at the end to clean up. Chrome implementation is planned for a later version (Although that may become obsolete with Manifest V3 and its effect on ad blockers).

### Add addons to addons_master_list.json

#### Adding Curseforge Addons
Add Curseforge addons to addon_master_list.json like so:

    {
    "DBM" : {
        "location" : "cf",
        "anchor_link" : "https://www.curseforge.com/wow/addons/deadly-boss-mods",
        "dl_url" : "https://www.curseforge.com/wow/addons/deadly-boss-mods/download",
        "last_updated" : ""
    },

#### Adding ElvUI 
Copy the following and add it to your addons_master_list.json and the script will take care of the rest.

    "ELVUI" : {
        "location" : "elvui",
        "anchor_link" : "https://www.tukui.org/welcome.php",
        "dl_url" : "https://www.tukui.org/downloads/elvui-",
        "current_version" : ""
    },

The script will also backup master_addon_list.json at the beginning of each run.

#### Adding TukUI
Copy the following and add it to your addons_master_list.json and the script will take care of the rest.

    "TUKUI" : {
        "location" : "tukui",
        "anchor_link" : "https://www.tukui.org/welcome.php",
        "dl_url" : "https://www.tukui.org/downloads/tukui-",
        "current_version" : ""
    },

The script will also backup master_addon_list.json at the beginning of each run.

## Copyright © 2022 Nicholas Johnson

Permission to use, copy, modify, distribute, and sell this software and its documentation for any purpose is hereby granted without fee, provided that the above copyright notice appear in all copies and that both that copyright notice and this permission notice appear in supporting documentation. No representations are made about the suitability of this software for any purpose.  It is provided "as is" without express or implied warranty.

Tested on **MacOS Ventura v13.1 Beta (22A5352e)** and **Windows 11 (Stable)** using **Firefox 106.0** with **uBlockOrigin 1.44.4**. Tested on Python 3.10.6, but should work with Python 3.+.

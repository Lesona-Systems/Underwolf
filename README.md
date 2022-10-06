# Underwolf

## Pull Requests are not only welcomed, they're encouraged.

Underwolf is my best answer to updating my World of Warcraft addons after the retirement of the CurseForge API (staying away from the CurseForge application). 

It utilizes Python's built-in webbrowser library to navigate to [CurseForge](https://www.curseforge.com/) download pages (as well as other direct download URLs, such as [Tukui](https://www.tukui.org) and [Trade Skill Master](https://www.tradeskillmaster.com/)) and download the specified addons (listed, one per line, in [url_list.txt](https://github.com/Lesona-Systems/Underwolf/blob/main/url_list.txt)), unzip them, and move them into the WoW addon folder.

## Requirements

The script currently **requires [Firefox](https://www.mozilla.org/en-US/firefox/new/) and [uBlock Origin](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/).** uBlock Origin "fast-forwards" the CurseForge imposed 5-second wait time (as well as other sites) before the download starts on the download pages (-_-). 

**Without uBlock Origin, the script will not work.**

Other than that, the script only uses built-in Python libraries.

**Underwolf currently has no addon version checking.** The script will redownload every addon each time it is run. This isn't ideal. I've found it worth logging in and seeing if any priority addons need updating and running then deciding whether or not to run the script. Version checking is a priority for future releases. 

Note that the script calls **taskkill** on Firefox process at the end to clean up. It will close any open Firefox processes when called. Chrome implementation is planned for a later version (Although that may become obsolete with Manifest V3 and its effect on ad blockers).

Tested on **MacOS Ventura v13.0 Beta (22A5352e)** and **Windows 11 (Stable)** using **Firefox 104.0.2** with **uBlockOrigin 1.44.4** as of September 22, 2022. Tested on Python v3.10.6, but should work with Python v3.x.x.

## Copyright © 2022 Nicholas Johnson

Permission to use, copy, modify, distribute, and sell this software and its documentation for any purpose is hereby granted without fee, provided thatthe above copyright notice appear in all copies and that both that copyright notice and this permission notice appear in supporting documentation. No representations are made about the suitability of this software for any purpose.  It is provided "as is" without express or implied warranty.

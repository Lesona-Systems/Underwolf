# Underwolf

Underwolf is my current best answer to updating my World of Warcraft addons after the retirement of the CurseForge API. It utilizes Python's built-in webbrowser library to navigate to [CurseForge](https://www.curseforge.com/) download pages and download the specified addons (listed, one per line, in [url_list.txt](https://github.com/Lesona-Systems/Underwolf/blob/main/url_list.txt)), unzip them, and move them into the WoW addon folder.

The script currently **requires [uBlock Origin](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/)** and it's ability to "fast-forward" the the website's imposed 5-second wait time before the download starts on the download pages (-_-). **Without uBlock Origin, the script will not work.**

**Underwolf currently has no addon version checking**, meaning that the script will redownload every addon each time it is run. This isn't ideal. I've found it worth logging in and seeing if any priority addons need updating and running then deciding whether or not to run the script. Version checking is a priority for future releases.

Note that the script calls **taskkill** on Firefox process at the end to clean up. It will close any open Firefox processes when called.

Tested on **MacOS Ventura v13.0 Beta (22A5352e)** and **Windows 11 (Stable)** using **Firefox 104.0.2** with **uBlockOrigin 1.44.4** as of September 22, 2022. Theoretically, it should work on Chrome as well.

## Copyright © 2022 Nicholas Johnson

Permission to use, copy, modify, distribute, and sell this software and its documentation for any purpose is hereby granted without fee, provided thatthe above copyright notice appear in all copies and that both that copyright notice and this permission notice appear in supporting documentation. No representations are made about the suitability of this software for any purpose.  It is provided "as is" without express or implied warranty.

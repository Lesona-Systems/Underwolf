# Underwolf

## Pull Requests are not only welcomed, they're encouraged.

Underwolf is my best answer to updating my World of Warcraft addons, both on and off CurseForge after the retirement of the CurseForge API (staying away from the CurseForge application). 

It utilizes Python's built-in webbrowser library to navigate to [CurseForge](https://www.curseforge.com/) download pages (as well as other direct download URLs, such as [Tukui](https://www.tukui.org) and [Trade Skill Master](https://www.tradeskillmaster.com/)) and download the specified addons (listed, one per line, in [url_list.txt](https://github.com/Lesona-Systems/Underwolf/blob/main/url_list.txt)), unzip them, and move them into the WoW addon folder. The script also uses Selenium for version checking.

## Requirements

The script currently **requires [Firefox](https://www.mozilla.org/en-US/firefox/new/) and [uBlock Origin](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/).** uBlock Origin "fast-forwards" the CurseForge imposed 5-second wait time (as well as other sites) before the download starts on the download pages (-_-). 

**Without uBlock Origin, the script will not work.**

Other than that, the script only uses Selenium and built-in Python libraries.

Note that the script calls **taskkill** on all Firefox processes at the end to clean up. Chrome implementation is planned for a later version (Although that may become obsolete with Manifest V3 and its effect on ad blockers).

Tested on **MacOS Ventura v13.0 Beta (22A5352e)** and **Windows 11 (Stable)** using **Firefox 104.0.2** with **uBlockOrigin 1.44.4**. Tested on Python 3.10.6, but should work with Python 3.5+.

## Copyright © 2022 Nicholas Johnson

Permission to use, copy, modify, distribute, and sell this software and its documentation for any purpose is hereby granted without fee, provided thatthe above copyright notice appear in all copies and that both that copyright notice and this permission notice appear in supporting documentation. No representations are made about the suitability of this software for any purpose.  It is provided "as is" without express or implied warranty.

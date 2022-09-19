import os
import webbrowser
from time import sleep

url_list = [
    "https://www.curseforge.com/wow/addons/deadly-boss-mods/download",
    "https://www.curseforge.com/wow/addons/details/download",
    "https://www.curseforge.com/wow/addons/weakauras-2/download",
    "https://www.curseforge.com/wow/addons/rarescanner/download",
    "https://www.curseforge.com/wow/addons/pawn/download",
    "https://www.curseforge.com/wow/addons/handynotes/download",
    "https://www.curseforge.com/wow/addons/all-the-things/download",
    "https://www.curseforge.com/wow/addons/handynotes-shadowlands/download",
    "https://www.curseforge.com/wow/addons/simulationcraft/download",
    ]

webbrowser.open_new("file://" +os.path.realpath("splash.html"))

for url in url_list:
    webbrowser.open_new_tab(url)
    sleep(5)

dl_dir = (os.path.expanduser('~') + "/Downloads")

dl_dir_count = 0
dl_dir_target = dl_dir_count + 9

for filename in os.listdir(dl_dir):
    dl_dir_count += 1

if dl_dir_count == dl_dir_target:
    for filename in os.listdir(dl_dir):
        print(filename)


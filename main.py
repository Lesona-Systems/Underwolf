import os, zipfile, webbrowser
from time import sleep, time

def main():
    # get current epoch for dl time comparison
    now = time()

    # list of download urls
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
        "https://www.tukui.org/downloads/elvui-12.90.zip",
        ]

    # open a new webbrowser, using splash.html page as an anchor for new tabs
    webbrowser.open_new("file://" + os.path.realpath("splash.html"))

    # logic for determining system type and assigning correct download directory on Mac & Windows
    dl_dir = get_download_path()

    # Set variables for current file count and target file count (so we can error check)
    dl_dir_count = 0
    dl_dir_target = dl_dir_count + len(url_list)

    # count number of files in Download directory before url_list downloads
    for filename in os.listdir(dl_dir):
        dl_dir_count += 1

    ##############
    # Note: the following REQUIRES uBlock Origin - it fast forwards through
    # the JS "your download will begin in n seconds" waiting message
    # and susequent (n) second wait time. We sleep for (2) seconds to safely
    # wait until the download starts, a feature I'm assuming has to do with
    # requiring browser tabs to be in focus to start a download.
    #############

    # open each download page to trigger the download
    for url in url_list:
        webbrowser.open_new_tab(url)
        sleep(2)

    zips = []

    if dl_dir_count == dl_dir_target:
        for filename in os.listdir(dl_dir):
            full_path = os.path.join(dl_dir, filename)
            if os.path.getmtime(full_path) > now :
                zips.append(full_path)
            else:
                continue
# untested below
    for filename in zips:
        with zipfile.ZipFile(filename,"r") as zipped_file:
            zipped_file.extractall(f"{dl_dir}\\addons")


# https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
def get_download_path():
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

if __name__ == "__main__":
    main()
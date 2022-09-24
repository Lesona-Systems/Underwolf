# Copyright © 2022 Nicholas Johnson

# Permission to use, copy, modify, distribute, and sell this software and its
# documentation for any purpose is hereby granted without fee, provided that
# the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation.  No representations are made about the suitability of this
# software for any purpose.  It is provided "as is" without express or
# implied warranty.

import os, zipfile, webbrowser, shutil
from time import sleep, time

def main():
    # get current epoch for dl time comparison (so we know which files to unzip)
    now = time()

    # parse url_list.txt
    url_list = open('url_list.txt', 'r').read().splitlines()

    # open a new webbrowser, using splash.html page as an anchor for new tabs
    webbrowser.open_new('file://' + os.path.realpath('splash.html'))

    # logic for determining system type and assigning
    # correct download directory on Mac & Windows
    dl_dir = get_download_path()
    print(f'Current download directory is {dl_dir}')

    if os.name == 'nt':
        dl_dir_addons = os.path.join(dl_dir, 'AddOns')
    else:
        dl_dir_addons = os.path.join(dl_dir, 'Addons')

    print(f'Successfully created temp dir at {dl_dir_addons}')

    # Set variables for current file count and target file count
    # (so we can error check) & count number of files in Download
    # directory before url_list downloads
    dl_dir_count = 0
    for filename in os.listdir(dl_dir):
        dl_dir_count += 1

    dl_dir_target = dl_dir_count + len(url_list)

    ##############
    # Note: the following REQUIRES uBlock Origin - it fast forwards
    # through the JS "your download will begin in n seconds" waiting
    # message and susequent (n) second wait time. We sleep for (2) 
    # seconds to wait until the download starts, a feature I'm
    # assuming has to do with requiring browser tabs to be in focus
    # to start a download.
    #############

    # open each download page to trigger the download
    for url in url_list:
        webbrowser.open_new_tab(url)
        sleep(2)
        dl_dir_count += 1
    sleep(2) # Wait for two more seconds to make sure downloads finish

    zips = []

    # For files in dl_dir, if the file's last-modified timestamp is later
    # than the timestamp recorded when we ran the script, assume those
    # files are the addons we just downloaded. I acknowledge that it's
    # bad logic. I'm working on it.
    if dl_dir_count == dl_dir_target:
        for filename in os.listdir(dl_dir):
            full_path = os.path.join(dl_dir, filename)
            if os.path.getmtime(full_path) > now :
                zips.append(full_path)
            else:
                continue

    # extract each addon to temp addon directory
    for filename in zips:
        with zipfile.ZipFile(filename,'r') as zipped_file:
            zipped_file.extractall(dl_dir_addons)

    addon_path = get_addon_path()

    # move addon temp dir and overwrite WoW addon dir
    try:
        shutil.rmtree(addon_path)
        shutil.move(dl_dir_addons, addon_path)
    except:
        print('Error')

    print('Killing browser processes...')
    os.system('taskkill /F /IM firefox.exe') # force kill running Firefox processes

    # remove downloaded addon zip files
    print('Cleaning downloads folder...')
    for filename in zips:
        os.remove(filename)

def get_download_path():
    # Just for the record, this is needlessly complicated
    # https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

# these addon paths are default install paths for World of Warcraft
def get_addon_path():
    if os.name == 'nt':
        wow_addon_path = 'C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns'
        return wow_addon_path
    else:
        wow_addon_path = '/Applications/World of Warcraft/_retail_/Interface/Addons'
        return wow_addon_path


if __name__ == '__main__':
    main()
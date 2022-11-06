import os
import zipfile
import webbrowser
import shutil
import json
import configparser
from time import sleep, time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class colors:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    # clear geckodriver.log
    if os.path.exists('geckodriver.log'):
        open('geckodriver.log', 'w').close

    # get current epoch for dl time comparison (so we know which files to unzip)
    now = time()

    config = configparser.ConfigParser()
    config.read('config.ini')

    wow_addon_directory = config['paths']['wow_addon_directory']
    firefox_download_directory = config['paths']['firefox_download_directory']
    ublock_xpi_path = config['paths']['ublock_xpi_path']


    master_list = 'addon_master_list.json'
    # check for addon_master_list.json. If it exists, back it up to backup_list.json. If not, 'throw' error.
    if os.path.exists('addon_master_list.json'):
        make_backup(master_list, 'backup_list.json')
    else:
        print(f'{colors.FAIL}ERROR!{colors.ENDC} {colors.BOLD}addon_master_list.json{colors.ENDC} not found!')
        print('\n Please check documentation at https://github.com/Lesona-Systems/Underwolf')
        print(f'{colors.FAIL}Quitting!{colors.ENDC}')
        quit()

    # read addon list to dict
    with open(master_list) as master:
        addon_dict = json.load(master)

    # initialize empty lists for addons and feedback
    url_list = []
    to_be_updated = []

    # read addon keys into dict. For each CF addon, call get_update_time() and
    # compare to last_updated in addon_master_list. If it's the same, move on.
    # If we've got different last_updated times, push addon to url_list[]
    # and update last_updated in addon_list.json.
    # Suprisingly, let's thank CF for tracking "last updated" in Unix time
    # in its front end so we don't have to do any conversions. :)
    for key in addon_dict.keys():
        name = addon_dict[key]
        if name['location'] == 'cf':
            print(f'Processing {key}...')
            current_version_time = get_update_time(name['anchor_link'], ublock_xpi_path)
            if current_version_time != name['last_updated']:
                url_list.append(name['dl_url'])
                to_be_updated.append(key)
                name['last_updated'] = current_version_time
            else:
                continue
        elif name['location'] == 'elvui':
            print(f'Processing {key}...')
            current_version = get_version_elvui(name['anchor_link'], ublock_xpi_path)
            if current_version != name['version']:
                dl_url = (f"{name['dl_url']}{current_version}.zip")
                url_list.append(dl_url)
                to_be_updated.append(key)
                name['version'] = current_version
        else:
            print(f'Processing {key}...')
            url_list.append(name['dl_url'])
            to_be_updated.append(name)

    # let user know which addons we're updating because feedback is nice
    if len(to_be_updated) > 0:
        print(f'{colors.GREEN}The following addons will be updated:{colors.ENDC}')
        print(to_be_updated)
    else:
        print(f'All World of Warcraft addons {colors.GREEN}up-to-date!{colors.ENDC}')
        quit()

    # determine system type and assign correct download directory
    dl_dir = get_download_path(firefox_download_directory)
    print(f'Using download directory at {colors.GREEN}{dl_dir}{colors.ENDC}')

    if os.name == 'nt':
        dl_dir_addons = os.path.join(dl_dir, 'AddOns')
    else:
        dl_dir_addons = os.path.join(dl_dir, 'Addons')

    # Intialize dl_dir_count to count number of files currently in Download directory
    # so we can "guess" when we're done. I haven't found a way to detect the difference
    # between an incomplete file download and a complete one. Neither Selenium nor Python's
    # built in webbrowser have this built in.
    dl_dir_count = 0
    for filename in os.listdir(dl_dir):
        dl_dir_count += 1

    # Target number of files/folders in Downloads directory equals (number of items)
    # currently in the folder plus the (number of items in url_list.txt)
    dl_dir_target = dl_dir_count + len(url_list)

    ##############
    # Note: the following REQUIRES uBlock Origin - it fast forwards
    # through the JS "your download will begin in n seconds" waiting
    # message and susequent (n) second wait time. We sleep for (2) 
    # seconds to wait until the download starts, a feature I'm
    # assuming has to do with requiring browser tabs to be in focus
    # to start a download. We can go ahead and increase this sleep
    # time if users are on a slow connection. 
    #############

    # open each download page to trigger the download
    for url in url_list:
        print(f'Opening {colors.GREEN}{url}{colors.ENDC}')
        webbrowser.open_new_tab(url)
        sleep(2)
        dl_dir_count += 1
    sleep(2) # Default is 2 for fast connections (over 25MBs) Wait for two more seconds and hope downloads are finished

    addon_zips = []

    # For files in dl_dir, if the file's "last-modified" timestamp is later
    # than the timestamp recorded when we ran the script, assume those
    # files are the addons we just downloaded. We're going to run into problems
    # if there are other downloads in Firefox/other browsers ongoing at the same
    # time. Maybe let's not do that? Add a warning to script start?

    if dl_dir_count == dl_dir_target:
        for filename in os.listdir(dl_dir):
            full_path = os.path.join(dl_dir, filename)
            if os.path.getmtime(full_path) > now :
                addon_zips.append(full_path)
            else:
                continue

    # extract each addon to temp addon directory in default download dir
    for filename in addon_zips:
        with zipfile.ZipFile(filename,'r') as zipped_file:
            zipped_file.extractall(dl_dir_addons)

    addon_path = get_addon_path(addon_zips, wow_addon_directory)

    # move addon temp dir and overwrite WoW addon dir
    # in the except block, we've gone back and forth over whether to clean up the downloaded
    # files and the unzipped, temp addons folder. If we've gotten this far, it seems dumb to delete
    # everything we've just downloaded. On the other hand, a graceful failure should leave the
    # system in the same state as it was before it ran. Problem for another day.
    try:
        shutil.rmtree(addon_path)
        shutil.move(dl_dir_addons, addon_path)
    except Exception:
        print(f'{colors.FAIL}Error during folder move process...{colors.ENDC}')
        clean_downloads(addon_zips)
        shutil.rmtree(dl_dir_addons)

    # Final cleanup and indicator of successful run
    kill_firefox()
    clean_downloads(addon_zips)
    # update addon_master_list.json with up-to-date "last_updated" timestamps
    update_master(addon_dict, master_list)
    print(f'Complete... \n{colors.GREEN}Script completed successfully!{colors.ENDC}')

def update_master(dict, file):
    with open(file, 'w') as json_file:
        json.dump(dict, json_file, indent=4)

def make_backup(file, file2):
    shutil.copy(file, file2)

def kill_firefox():
    '''Kill all Firefox browser processes'''
    print('Killing browser processes...')
    if os.name == 'nt':
        os.system('taskkill /F /IM firefox.exe /T')
    else:
        os.system('pkill -f firefox')

def clean_downloads(list):
    '''For filename in list, delete the file.'''
    print(f'Cleaning {colors.GREEN}Downloads{colors.ENDC} folder...')
    for filename in list:
        os.remove(filename)

def get_download_path(path):
    '''Determine system type: Windows or MacOS. For Windows, get the Downloads folder GUID from the registry and
        programatically get the "Downloads" path. For MacOS, simple expand os.path using os.path.expanduser and 
        join with "Downloads"'''
    # Just for the record, this is needlessly complicated
    # https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
    if path == '':
        print('No custom download directory detected in config.ini. Using default download directory.')
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        return path

def get_addon_path(addon_list, wow_addon_directory):
    if os.name == 'nt':
        if os.path.isdir(wow_addon_directory):
            return wow_addon_directory
        else:
            print(f'{colors.FAIL}Error!{colors.ENDC} {wow_addon_directory} does not exist!')
            print(f'Ensure you have run World of Warcraft and logged into a character at least once to generate the required folder structure.')
            clean_downloads(addon_list)
            kill_firefox()
            quit()
        return wow_addon_path
    else:
        if os.path.isdir(wow_addon_directory):
            return wow_addon_directory
        else:
            print(f'{colors.FAIL}Error!{colors.ENDC}')
            print(f'{colors.BOLD}{wow_addon_directory}{colors.ENDC} does not exist!')
            print(f'Ensure you have run World of Warcraft and logged into a character at least once to generate the required folder structure.')
            print(f'{colors.FAIL}Quitting!{colors.ENDC}')
            clean_downloads(addon_list)
            kill_firefox()
            quit()

def start_browser():
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    browser = webdriver.Firefox(options=opts)
    return browser
    
def get_update_time(url, ublock_xpi_path):
    browser = start_browser()

    if os.name == 'nt':
        # Windows panics if we don't pass this as a raw string
        ublock = fr"{ublock_xpi_path}"
    else:
        ublock = ublock_xpi_path

    browser.install_addon(ublock)
    browser.get(url)

    xpath = browser.find_element(By.XPATH, "//abbr[@class='tip standard-date standard-datetime']")
    last_updated = xpath.get_attribute("data-epoch")
    browser.close()

    return last_updated

def get_version_elvui(url, ublock_xpi_path):
    driver = start_browser()

    if os.name == 'nt':
        # Windows panics if we don't pass this as a raw string
        ublock = fr"{ublock_xpi_path}"
    else:
        ublock = ublock_xpi_path

    driver.install_addon(ublock)
    driver.get(url)

    version = [my_elem.get_attribute("innerText") for my_elem in WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[2]/div/div/ul/li/div[4]/div/a[2]/span")))]

    version = (version[0])
    
    driver.close()

    return version

if __name__ == '__main__':
    main()

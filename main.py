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
    BLUE = '\033[94m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():

    bypass_warning = ""
    print(r"""
     _    _               _                                    _    __ 
    | |  | |             | |                                  | |  / _|
    | |  | |  _ __     __| |   ___   _ __  __      __   ___   | | | |_ 
    | |  | | | '_ \   / _` |  / _ \ | '__| \ \ /\ / /  / _ \  | | |  _|
    | |__| | | | | | | (_| | |  __/ | |     \ V  V /  | (_) | | | | |  
     \____/  |_| |_|  \__,_|  \___| |_|      \_/\_/    \___/  |_| |_|  
                                                                        
    """)
    print(f'{colors.BOLD}{colors.BLUE}This script will close any open Firefox processes. Please ensure Firefox is closed and any in-progress downloads are finished before continuing!{colors.ENDC}')

    while bypass_warning != "y":
        bypass_warning = str(input(f'Are you ready to continue? ({colors.GREEN}{colors.BOLD}y{colors.ENDC}) or ({colors.FAIL}{colors.BOLD}n{colors.ENDC}): ').lower())
        if bypass_warning == "n":
            print('Quitting!')
            quit()
        else:
            continue
        
    # clear geckodriver.log
    if os.path.exists('geckodriver.log'):
        open('geckodriver.log', 'w').close

    # get current epoch for download time comparison
    now = time()

    config = configparser.ConfigParser()
    config.read('config.ini')

    wow_addon_directory = config['paths']['wow_addon_directory']
    firefox_download_directory = config['paths']['firefox_download_directory']
    ublock_xpi_path = config['paths']['ublock_xpi_path']


    master_list = 'addon_master_list.json'
    # check for addon_master_list.json. If it exists, back it up to backup_list.json. If not, inform user.
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

    # initialize empty lists for addons (url_list[]) and user feedback (to_be_updated[])
    url_list = []
    tukui_url_list = []
    to_be_updated = []

    # read addon keys into dict. For each CF addon, call get_cf_update_time() and
    # compare to last_updated in addon_master_list. If it's the same, move on.
    # If we've got different last_updated times, push addon to url_list[]
    # and update last_updated in addon_list.json.
    # Suprisingly, let's thank CF for tracking "last updated" in Unix time
    # in its legaccy front end so we don't have to do any conversions while it's still up.
    for key in addon_dict.keys():
        name = addon_dict[key]
        if name['location'] == 'cf':
            print(f'Processing {key}...')
            current_version_time = get_cf_update_time(name['anchor_link'], ublock_xpi_path)
            if current_version_time != name['last_updated']:
                url_list.append(name['dl_url'])
                to_be_updated.append(key)
                name['last_updated'] = current_version_time
            else:
                continue
    # Here we do the same for TukUI and ElvUI, with the only difference being we check
    # current_version instead of current version time.
        elif name['location'] == 'tukui':
            print(f'Processing {key}...')
            current_version = get_version_tuk_addon(name['anchor_link'], ublock_xpi_path)
            if current_version != name['current_version']:
                dl_url = (f"{name['dl_url']}")
                tukui_url_list.append(dl_url)
                to_be_updated.append(key)
                name['current_version'] = current_version
    # in the else block, we take care of any addons that aren't from CF or TukUI.
    # No version checking here, but it gives advanced users some leeway if they have a direct
    # download link that we haven't implemented version checking for.
        else:
            print(f'Processing {key}...')
            url_list.append(name['dl_url'])
            to_be_updated.append(key)

    # Print list of addons to be updated for user feedback
    if len(to_be_updated) > 0:
        print(f'{colors.GREEN}The following addons will be updated:{colors.ENDC}')
        for addon in to_be_updated:
            print(f'{colors.BOLD}{addon}{colors.ENDC}')
    else:
        print(f'All World of Warcraft addons {colors.GREEN}up-to-date!{colors.ENDC} \n See you in Azeroth!')
        quit()

    # determine system type and assign correct download directory
    dl_dir = get_download_path(firefox_download_directory)
    print(f'Using download directory at {colors.GREEN}{dl_dir}{colors.ENDC}')

    # create temporary addon folder per OS, since WoW capitalizes its folders
    # differently depending on OS present
    if os.name == 'nt':
        dl_dir_addons = os.path.join(dl_dir, 'AddOns')
    else:
        dl_dir_addons = os.path.join(dl_dir, 'Addons')

    # Intialize dl_dir_count to count number of files currently in Download directory
    # so we can infer when we're done. I haven't found a way to detect the difference
    # between an incomplete file download and a complete one. Neither Selenium nor Python's
    # built in webbrowser lib have this built-in.
    dl_dir_count = 0
    for filename in os.listdir(dl_dir):
        dl_dir_count += 1

    # Target number of files/folders in Downloads directory equals (dl_dir_count)
    # currently in the folder plus the number of items in url_list[]
    dl_dir_target = dl_dir_count + len(url_list) +len(tukui_url_list)

    ##############
    # Note: the following REQUIRES uBlock Origin - it fast forwards
    # through the JS "your download will begin in n seconds" waiting
    # message and susequent (n) second wait time. We sleep for (2) 
    # seconds to wait until the download starts, a feature I'm
    # assuming has to do with requiring browser tabs to be in focus
    # to start a download. We can go ahead and increase this sleep
    # time if users are on a slow connection. 
    #############

    # open each download page to trigger the download & wait predetermined
    # time for dl to start
    for url in url_list:
        print(f'Opening {colors.GREEN}{url}{colors.ENDC}')
        webbrowser.open_new_tab(url)
        sleep(2)
        dl_dir_count += 1
    sleep(3) # Default is 3 for fast connections (over 25Mbs)

    for url in tukui_url_list:
        print(f'Opening {colors.GREEN}{url}{colors.ENDC}')
        download_tuk_addon(url, ublock_xpi_path)
        dl_dir_count += 1

    addon_zips = []

    # For files in dl_dir, if the file's "last-modified" timestamp is later
    # than the timestamp recorded when we ran the script, assume those
    # files are the addons we just downloaded.

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

    # move addon temp dir and overwrite WoW's addon dir
    # in the except block, we've gone back and forth over whether to clean up the downloaded
    # files and the unzipped, temp addons folder if an exception is raised. If we've gotten this
    # far, it seems dumb to delete everything we've just downloaded. On the other hand, a 
    # graceful failure should leave the system in the same state as it was before it ran. 
    # Problem for another day.
    try:
        shutil.copytree(dl_dir_addons, addon_path, dirs_exist_ok=True)
    except Exception:
        print(f'{colors.FAIL}Error during folder move process...{colors.ENDC}')
        clean_downloads(addon_zips)
        shutil.rmtree(dl_dir_addons)

    # Final cleanup and indicator of successful run
    final_count = len(to_be_updated)
    kill_firefox()
    clean_downloads(addon_zips)
    clean_temp_addon_folder(dl_dir_addons)
    # update addon_master_list.json with up-to-date "last_updated" timestamps
    update_master(addon_dict, master_list)
    print(f'{final_count} addons updated. \n{colors.GREEN}Script completed successfully!{colors.ENDC} See you in Azeroth!')

def update_master(dict, file):
    '''Write input dictionary to file'''
    with open(file, 'w') as json_file:
        json.dump(dict, json_file, indent=4)

def make_backup(file, filename):
    '''Copy file to filename'''
    shutil.copy(file, filename)

def kill_firefox():
    '''Kill all Firefox browser processes'''
    print('Killing browser processes...')
    if os.name == 'nt':
        os.system('taskkill /F /IM firefox.exe /T')
    else:
        os.system('pkill -f firefox')

def clean_downloads(list):
    '''For filename in list, delete the file.'''
    print(f'Cleaning {colors.GREEN}Downloaded{colors.ENDC} zips...')
    for filename in list:
        os.remove(filename)

def clean_temp_addon_folder(path):
        print(f'Cleaning {colors.GREEN}Temp Addon{colors.ENDC} folder...')
        shutil.rmtree(path)


def get_download_path(path):
    '''Determine system type: Windows, MacOS, or Linux. For Windows, get the Downloads folder GUID from the registry and
        programatically get the "Downloads" path. For MacOS/Linux, expand os.path using os.path.expanduser and 
        join with "Downloads"'''
    # Just for the record, this is needlessly complicated
    # https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
    if path == '':
        print('No custom download directory detected in config.ini. Using the default OS download directory.')
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
    '''Start a headless instance of Selenium and return the browser instance
    that accepts Selenium methods.'''
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    return driver

def start_visible_browser():
    driver = webdriver.Firefox()
    return driver

def get_cf_update_time(cf_url, ublock_xpi_path):
    '''Start an instance of the Selenium browser, activate the uBlock origin .xpi file
    from the provided ublock_xpi_path, navigate to the provided curseforge url (cf_url),
    and grab and return the addon's updated epoch from the url.'''
    driver = start_browser()

    if os.name == 'nt':
        # Windows panics if we don't pass this as a raw string
        ublock = fr"{ublock_xpi_path}"
    else:
        ublock = ublock_xpi_path

    driver.install_addon(ublock)
    driver.get(cf_url)

    xpath = driver.find_element(By.XPATH, "//abbr[@class='tip standard-date standard-datetime']")
    last_updated = xpath.get_attribute("data-epoch")
    driver.close()

    return last_updated

def get_version_tuk_addon(tuk_url, ublock_xpi_path):
    '''Start an instance of the Selenium browser, activate the uBlock origin .xpi file
    from the provided ublock_xpi_path, navigate to the Tukui Homepage url (tuk_url),
    and grab and return the addon's version number from the url.'''
    driver = start_browser()

    if os.name == 'nt':
        # Windows panics if we don't pass this as a raw string
        ublock = fr"{ublock_xpi_path}"
    else:
        ublock = ublock_xpi_path

    driver.install_addon(ublock)
    driver.get(tuk_url)

    # Wait for addon version number to be visable, then grab it from the download button.
    version_list = [my_elem.get_attribute("innerText") for my_elem in WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="download-button"]')))]
    # the above returns a list by default, so reassign "version" to the the first element in the list.
    version_item = version_list[0]

    version_split = version_item.split()
    current_version = (version_split[-1])

    driver.close()

    return current_version

def download_tuk_addon(tuk_url, ublock_xpi_path):
    driver = start_visible_browser()

    if os.name == 'nt':
        ublock = fr"{ublock_xpi_path}"
    else:
        ublock = ublock_xpi_path

    driver.install_addon(ublock)
    driver.get(tuk_url)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="download-button"]')))
    sleep(2)
    driver.find_element(By.XPATH, '//*[@id="download-button"]').click();
    sleep(5)

    driver.close()

if __name__ == '__main__':
    main()

from selenium import webdriver
from selenium.webdriver.common.by import By

url = "https://www.curseforge.com/wow/addons/deadly-boss-mods"

browser = webdriver.Firefox()
uBlock = "/Users/nick/Library/Application Support/Firefox/Profiles/wr8z2mm6.default-release/extensions/uBlock0@raymondhill.net.xpi"

browser.install_addon(uBlock, temporary=True)

browser.get(url)

xpath = browser.find_element(By.XPATH, "//abbr[@class='tip standard-date standard-datetime']")
epoch = xpath.get_attribute("data-epoch")
print(epoch)

browser.close()
quit()

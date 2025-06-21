from seleniumbase import Driver, get_driver

# driver = Driver(uc=True, incognito=True)




# options = get_driver.ChromeOptions()
#options.add_arguments("start-maximized")
chromme_profile = r"D:\Programming\Projects\SIH\Social_media_scraper\chromedata\chromeprofile"

driver = Driver(uc=True, user_data_dir=chromme_profile)
driver.get("https://x.com/elonmusk")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
import time
import requests
import os
import shutil
from PIL import Image
import json
import undetected_chromedriver as uc
from seleniumbase import Driver, get_driver



# chrome_options = uc.ChromeOptions()
# # chrome_options.add_argument("--remote-debugging-port=8989")
# chrome_options.add_argument('--user-data-dir=D:\Programming\Projects\SIH\Social_media_scraper\chromedata\chromeprofile')
# chrome_driver = r"D:\Programming\Projects\SIH\Social_media_scraper\chromedata\chromedriver.exe"
# chrome_options.headless=True
# opt.add_experimental_option("debuggerAddress","localhost:8989")
# chrome_options.add_experimental_option("detach", True)
chromme_profile = r"D:\Programming\Projects\SIH\Social_media_scraper\chromedata\chromeprofile"
driver =  Driver(uc=True, user_data_dir=chromme_profile,headless=False)
# driver.maximize_window()
# window_width, window_height = driver.get_window_size()["width"],driver.get_window_size()["height"]
# print(window_height)



def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",element, s)
    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 2px solid red;")
    time.sleep(1)
    apply_style(original_style)

def modify_user_name(username):
    username.strip()
    if username[0] == '@':
        username = username[1:]
    if "https://" in username:
        username = username.split("/")[3]
    return username


def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        # Empty the directory if it already exists
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory
            except Exception as e:
                pass  # Silently pass on any exceptions

def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {url} to {save_path}")
    else:
        print(f"Failed to download {url}")

def download_links(links_list,dir_path):
    for idx, url in enumerate(links_list):
        file_name = f"image_{idx + 1}.jpg"
        save_path = os.path.join(dir_path, file_name)
        download_image(url, save_path)



def scrape_media_fast(username,scrape_factor = 10):
    username = modify_user_name(username)
    driver.get(f"https://x.com/{username}/media")
    time.sleep(5)
    driver.execute_script("document.body.style.zoom='200%'")


    gallery_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div")
    
    img_elements = gallery_element.find_elements(By.TAG_NAME, "img")
    img_srcs = [img.get_attribute("src") for img in img_elements]

    while len(img_srcs)<scrape_factor:
        driver.execute_script('window.scrollBy(0, 400)')
        time.sleep(2)
        
        temp_img_elements =gallery_element.find_elements(By.TAG_NAME, "img")
        for temp_img_element in temp_img_elements:
            if temp_img_element.get_attribute("src") not in img_srcs:
                img_srcs.append(temp_img_element.get_attribute("src"))

        # print(type(img_elements))
        # print(len(img_srcs))
    img_srcs = img_srcs[:scrape_factor]
    driver.execute_script("document.body.style.zoom='100%'")
    return img_srcs

def retrieve_post_data(link,savepath):

    driver.get(link)
    # driver.execute_script("document.body.style.zoom='100%'")
    time.sleep(5)
    tweet_text_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article")
    tweet_text_element.screenshot(f"temp.png")
    # for i in range(1,3):
    #     driver.execute_script(f'window.scrollBy(0,{450})')
    #     time.sleep(5)
    #     tweet_text_element.screenshot(f"temp{i+1}.png")
    #     print(tweet_text_element.location)


    im = Image.open("temp.png")
    width, height = im.size
    im.crop((0, 0, width*(1), height)).save(savepath)
    # data_name = savepath.split('\\')[-1]
    data_dict = {}

    try:
        tweet_text_element = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div')
        tweet_text = tweet_text_element.text
    except:
        tweet_text = " "

    data_dict["text"]=tweet_text

    try:
        tweet_dt = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div[1]/a/time').text
    except:
        tweet_dt = "unfetchable"
        pass

    data_dict["date_time"]=tweet_dt

    try:
        embedding_links_element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[2]/div/div/div[2]/div')
        embedding_links = embedding_links_element.find_elements(By.TAG_NAME, "a")
        embedding_links =[a.get_attribute("href") for a in embedding_links ]
    except:
        embedding_links = ["unfetchable or empty"]
        pass
    
    data_dict["tweet_embeddings"]=embedding_links
    print("saved", savepath)
    # print(embedding_links)
    return data_dict
    # time.sleep(5)

def dump_post_list_data(username,links,tweets_data_directory=None):

    username = modify_user_name(username)

    if tweets_data_directory==None:
        data_directory = os.path.join(os.path.dirname(__file__),"Scraped_Data",username)
        tweets_data_directory = os.path.join(data_directory,"posts")
        create_directory(tweets_data_directory)

    data_dict ={username:{}}

    for i,link in enumerate(links):
       
        data_dict[username].update({f"{i+1}":{}})
        data_dict[username][f"{i+1}"] =  retrieve_post_data(link,savepath=tweets_data_directory+f"\{i+1}.png")
        data_dict[username][f"{i+1}"].update({"link":f"{link}"})

    with open(f'{tweets_data_directory}\\data.json', 'w') as fp:
        json.dump(data_dict, fp)
    try:
        os.remove("temp.png")
    except:
        pass

def scrape_posts(username, scrape_factor=2, retweet_include = False):

    def check_link(link):
        if retweet_include==False:
            status_text = f"https://x.com/{username}/status/"
            if status_text in link:
                return True
            else:
                return False
        else:
            if "status" in link:
                return True
            else:
                False

    username = modify_user_name(username)
    driver.get(f"https://x.com/{username}/")
    time.sleep(5)
    driver.execute_script("document.body.style.zoom='100%'")

    post_gallery_element =  driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div')
    a_elements = post_gallery_element.find_elements(By.TAG_NAME, "a")
    for a in a_elements:
        inner_html = a.get_attribute("innerHTML")
        if "<time" in inner_html:  # Check if the inner HTML contains a time tag
            print("Time tag found:", inner_html)
    
    href_elements = [a.get_attribute("href") for a in a_elements ]
    
    href_elements = [h for h in href_elements if check_link(h)]
    href_elements = ["/".join(h.split("/")[:6]) for h in href_elements if check_link(h)]
    href_elements = list(set(href_elements))

    # print(href_elements)

    while len(href_elements)< scrape_factor:
        driver.execute_script('window.scrollBy(0, 400)')
        time.sleep(0.5)

        temp_href_elements = post_gallery_element.find_elements(By.TAG_NAME, "a")
        temp_href_elements = [a.get_attribute("href") for a in temp_href_elements]
        temp_href_elements = [h for h in temp_href_elements if check_link(h)]
        temp_href_elements = ["/".join(h.split("/")[:6]) for h in temp_href_elements if check_link(h)]

        for temp_href_element in temp_href_elements:

            if temp_href_element not in href_elements:
                href_elements.append(temp_href_element)
        
        print(f"tweet links scraped : {len(href_elements)}/{scrape_factor}")

    href_elements = href_elements[:scrape_factor]
    print(href_elements)
    dump_post_list_data(links=href_elements, username=username)
    return href_elements


def retrieve_account_info(username, save_json_fp=os.path.join(os.path.dirname(__file__),"Scraped_Data")):
    username = modify_user_name(username)
    save_json_fp = os.path.join(save_json_fp,username)
    driver.get(f"https://x.com/{username}/")
    time.sleep(5)
    data_dict = {}
    try:
        name = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/span/span[1]").text
    except:
        name = "not fetchable"
    data_dict["name"] = name

    try:
        user_name = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div[1]/div/div[2]/div/div/div/span").text
    except:
        user_name = "not fetchable"
    data_dict["username"] = user_name

    try:
        bio = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div").text
    except:
        bio = "not fetchable"
    data_dict["bio"] = bio

    try:
        location = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span[1]/span").text
    except:
        location = "not fetchable"
    data_dict["location"] = location

    try:
        bio_link = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/a").get_attribute("href")
    except:
        bio_link = "not fetchable"
    data_dict["bio_link"] = bio_link

    try:
        join_date = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span[2]/span").text
    except:
        join_date = "not fetchable"
    data_dict["join_data"] = join_date

    try:
        following = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[1]/a/span[1]/span").text
    except:
        following = "not fetchable"
    data_dict["following"] = following
        
    try:
        followers = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[2]/a/span[1]/span").text
    except:
        followers = "not fetchable"
    data_dict["followers"] = followers

    # print(data_dict)
    if not os.path.exists(save_json_fp):
        os.makedirs(save_json_fp)
    with open(f'{save_json_fp}\\account_info.json', 'w') as fp:
        json.dump(data_dict, fp)
    return data_dict
    

def retrive_account_follower(username,scrape_factor=10,save_json_fp=os.path.join(os.path.dirname(__file__),"Scraped_Data")):
    username = modify_user_name(username)
    save_json_fp = os.path.join(save_json_fp,username)

    driver.get(f"https://x.com/{username}/followers")
    time.sleep(5)

    follower_users_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section")
    follower_users = follower_users_element.find_elements(By.TAG_NAME, "a")
    follower_users = [a.get_attribute("href") for a in follower_users]
    follower_users = list(set(follower_users))

    while len(follower_users)<scrape_factor:
        driver.execute_script('window.scrollBy(0, 200)')
        time.sleep(2)
        
        temp_follower_elements =follower_users_element.find_elements(By.TAG_NAME, "a")
        temp_follower_elements = [a.get_attribute("href") for a in temp_follower_elements]
        
        for temp_follower_element in temp_follower_elements:
            if temp_follower_element not in follower_users:
                follower_users.append(temp_follower_element)
            print(len(follower_users))
        
    follower_users = follower_users[:scrape_factor]
    print(follower_users)

    data_dict = {}
    data_dict[username] = follower_users

    if not os.path.exists(save_json_fp):
        os.makedirs(save_json_fp)
    with open(f'{save_json_fp}\\follower_info.json', 'w') as fp:
        json.dump(data_dict, fp)
    return data_dict






def retrive_account_following(username, scrape_factor=10, save_json_fp=os.path.join(os.path.dirname(__file__),"Scraped_Data")):
    username = modify_user_name(username)
    save_json_fp = os.path.join(save_json_fp,username)

    driver.get(f"https://x.com/{username}/following")
    time.sleep(5)

    following_users_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section")
    following_users = following_users_element.find_elements(By.TAG_NAME, "a")
    following_users = [a.get_attribute("href") for a in following_users]
    following_users = list(set(following_users))

    while len(following_users)<scrape_factor:
        driver.execute_script('window.scrollBy(0, 200)')
        time.sleep(2)
        
        temp_following_elements =following_users_element.find_elements(By.TAG_NAME, "a")
        temp_following_elements = [a.get_attribute("href") for a in temp_following_elements]
        
        for temp_following_element in temp_following_elements:
            if temp_following_element not in following_users:
                following_users.append(temp_following_element)
            print(len(following_users))
    
    following_users = following_users[:scrape_factor]
    print(following_users)
    data_dict = {}
    data_dict[username] = following_users

    if not os.path.exists(save_json_fp):
        os.makedirs(save_json_fp)
    with open(f'{save_json_fp}\\following_info.json', 'w') as fp:
        json.dump(data_dict, fp)
    return data_dict




# username = modify_user_name(username)
# data_directory = os.path.join(os.path.dirname(__file__),"Scraped_Data",username)
# # create_directory(data_directory)
# tweets_data_directory = os.path.join(data_directory,"posts")
# create_directory(tweets_data_directory)

# media_links =['https://x.com/elonmusk/status/1827163562839507219','https://x.com/premium/status/1623411400545632256','https://x.com/elonmusk/status/1827155331002007843', 'https://x.com/elonmusk/status/1827206038778458451', 'https://x.com/elonmusk/status/1827198275021050113', 'https://x.com/elonmusk/status/1827174670375735491', 'https://x.com/elonmusk/status/1827172947280249138', 'https://x.com/elonmusk/status/1827167868733059171', 'https://x.com/elonmusk/status/1827163562839507219', 'https://x.com/elonmusk/status/1827162546685583658', 'https://x.com/elonmusk/status/1827156608066924980', 'https://x.com/elonmusk/status/1827055998286319711', 'https://x.com/elonmusk/status/1827055547599712757', 'https://x.com/elonmusk/status/1827055853083750531', 'https://x.com/elonmusk/status/1827045479299133699', 'https://x.com/elonmusk/status/1827030749884612898', 'https://x.com/elonmusk/status/1827012570357612835', 'https://x.com/elonmusk/status/1827008827226497372', 'https://x.com/elonmusk/status/1826682757755666705', 'https://x.com/elonmusk/status/1826633760651313225', 'https://x.com/elonmusk/status/1826630645319373112', 'https://x.com/elonmusk/status/1826619232580501943']
# media_links = scrape_posts(username, scrape_factor=30, retweet_include=False)

# dump_post_list_data(username=username,links=media_links[:])
# # username = "@BillGates"
# retrive_account_follower(username=username)
# retrive_account_following(username=username)
# retrieve_account_info(username=username)

# print(len(media_links))

def scrape_DM_ss(link,username = None,save_folder_fp =None, scrape_factor = 10, scroll_factor = 25):
    
    try:
        driver.get(link)
        time.sleep(5)
    except:
        print("There is some kind of error in link plz recheck")
        return
    
    if username==None:
        try:
            username = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[1]/div/div/div/div/div[1]/div").text
        except:
            print("There is some kind of error with the link please try again")
            return
        
    print(username)
    # return
    if save_folder_fp==None:
        save_folder_fp = os.path.join(os.path.dirname(__file__),"Scraped_messages", username)
        create_directory(save_folder_fp)
    
    
    try:
    # chat_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div")
        chat_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[2]/div/div/div")
        highlight(chat_box)
        button_elem = chat_box.find_elements(By.TAG_NAME,"button")
        button_elem = [elem for elem in button_elem if elem.get_attribute("data-testid")=='messageEntry']
        button_elem = button_elem[-1]
        highlight(button_elem)
        button_elem.click()
    except:
        print("There is some kind of error in link plz recheck")
        return

    # time.sleep(5)
    i = 0
    while i<scrape_factor:
        chat_box.screenshot(f"{save_folder_fp}\\{i+1}.png")
        time.sleep(1)
        [button_elem.send_keys(Keys.UP) for i in range(scrape_factor)]
        time.sleep(1)
        print(f"saved message window {i+1}/{scrape_factor}")
        i +=1

# link = "https://x.com/messages/1486749350399123460-1747661009807171584"
# scrape_DM_ss(link)

username = "@elonmusk"
scrape_posts(username=username,scrape_factor=10)
driver.quit()

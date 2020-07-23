"""
    @file: soundcloud.py
    @author: Nish Gowda
    @date: 07/22/20
    @about: Scrapes soundcloud to grab the links of all the songs in a given playlist
    and then autonomously visits a website that downloads soundcloud songs
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import os
import sys
from dotenv import load_dotenv
from os.path import join, dirname

class SoundcloudPlugin():

    def __init__(self):
        self.directory_name = ''
        self.tracks = {}
        env_path = join(dirname(__file__), 'secrets.env')
        load_dotenv(env_path)
        self.playlist_url = os.environ.get("PLAYLIST_URL")
        self.chrome_driver = os.environ.get("CHROME_DRIVER")
        self.parent_dir = os.environ.get("PARENT_DIR")

    # using beautiful soup and selenium to find all the items in a playlist in soundcloud and add the song name and their links
    def scrape(self):
        driver = webdriver.Chrome(self.chrome_driver)
        driver.get(self.playlist_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all("li", class_="trackList__item sc-border-light-bottom")
        track_url = []
        for x in results:
            div = x.find_all("div", class_="trackItem g-flex-row sc-type-small sc-type-light")
            for z in div:
                final_div = z.find_all("div", class_="trackItem__content sc-truncate")
                for ref in final_div:
                    href = ref.find("a", class_="trackItem__trackTitle sc-link-dark sc-font-light",href=True)
                    link = ("https://soundcloud.com" + href['href'])
                    self.tracks.update({href.text: link})
                    
        driver.close()
        self.download_soundcloud(self.tracks)

    # use selenium to automate the process of clicking through klickaud.com to download the songs
    def download_soundcloud(self, links):
        for track in links.keys():
            driver = webdriver.Chrome(self.chrome_driver)
            driver.get("https://www.klickaud.co/")
            inputElement = driver.find_element_by_name("value")
            inputElement.clear()
            inputElement.send_keys(links[track])
            inputElement.submit()
            try:
                download_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "dlMP3"))
                )
            finally:
                download_element.click()
                print('Downloading ' + track + "...")
    
    # make the directory in the same directory as the projects and move all the downloaded songs there
    # Note this will work if there aren't any .mp3 files already in downloads folder
    def make_directories(self):
        directory_name = self.directory_name
        parent_dir = self.parent_dir
        path = os.path.join(dirname(__file__), directory_name)
        source_files = os.listdir(parent_dir)
        os.mkdir(path)
        for file in source_files:
            if file.endswith(".mp3"):
                shutil.move(os.path.join(parent_dir, file), os.path.join(path,file))
        print("Moved files to created directory: " + str(path))

if __name__ == "__main__":
    soundcloud = SoundcloudPlugin()
    soundcloud.directory_name = sys.argv[1]
    soundcloud.scrape()
    soundcloud.make_directories()
    

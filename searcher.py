import os
import sys
import io
import time
import requests
import hashlib
import logger as l
import threading

from PIL import Image, UnidentifiedImageError

from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from glob import glob


if not os.path.exists('images/'):
    os.mkdir('images/')
spath = 'images/'


SLEEP_BETWEEN_INTERACTIONS = 0.1
SLEEP_BEFORE_MORE = 5
IMAGE_QUALITY = 85


__useSession = False


class Session(object):
    def __init__(self, webdriver, pattern, path, number_of_images,  headless_mode=True, unique_img_name=True,  csplit=False, unverified=False, threads = 1):
        l.logI('Starting new session..')

        self.__webdriver = webdriver
        self.__pattern = pattern
        self.__path = path
        self.__number_of_images = number_of_images
        self.__headless_mode = headless_mode
        self.__unique_img_name = unique_img_name
        self.__unverified = unverified
        self.__threads = threads
        self.__csplit = csplit
        pass

   
    def __action(self):
        s = Searcher(   webdrv=self.__webdriver, pattern=self.__pattern,
                        output_path=self.__path, number_of_images=self.__number_of_images, 
                        headless_mode = self.__headless_mode, unique_img_name = self.__unique_img_name,
                        unverified = self.__unverified)
        s.searchAndDownload( self.__pattern, self.__path, self.__number_of_images)
        s.quit()
        pass


    def run(self, threads_number : int = 1):
        # if self.__number_of_images > 500:
            # threads_number = 10
        # else:
            # threads_number = self.__threads
        threads_number = self.__threads
        # for t in range (1, threads_number+1):
            # thread = threading.Thread( target=self.__action, args= ( ));
            # thread.start()
        # pass
        thread_list = []
        for i in range(threads_number):
            thread_list.append(threading.Thread(target=self.__action, args=()));
        
        for t in thread_list:
            t.start()

        # wait for the thread_workers to finish
        for t in thread_list:
            t.join()

        pass



class Searcher(object):
    """ Create object with specific webdriver."""
    def __init__(self, webdrv, pattern, output_path, number_of_images, headless_mode=True, unique_img_name=True, csplit=False, unverified=False):
        l.logI('Starting ' + webdrv + ' webdriver..')
        if (webdrv == 'gecko'):
            options = Options()
            if headless_mode == True:
                options.headless = True
            self.__wd = wd.Firefox(options=options)
        elif(webdrv == 'chrome'):
            options = Options()
            if headless_mode == True:
                options.add_argument('--headless')
            # Last I checked this was necessary.
            options.add_argument('--disable-gpu')
            self.__wd = wd.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            sys.exit(1)
        self.__pattern = pattern
        self.__output_path = output_path
        self.__number_of_images = number_of_images
        self.__unique_img_name = unique_img_name
        self.__split_to_class = csplit
        self.__unverified = unverified
        self.__number_of_saved = 0
        self.makeOutDir()

        if (unverified == True):
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable InsecureRequestWarning

        l.logI('The ' + webdrv + ' webdriver ready to work!')
        pass


    ################################################################################################################################
    ### MAKE OUTPUT DIRECTORY TO STORE DOWNLOADED IMAGES
    def makeOutDir(self):
        if not os.path.exists(self.__output_path):
            os.mkdir(self.__output_path)
        spath = self.__output_path # 'images/'
        pass

    ################################################################################################################################
    ### FETCH URLS OF IMAGES
    def fetchUrls(self, query: str, max_links_to_fetch: int,
                  sleep_between_interactions: int = 1,
                  ):

        # Build the Google Query.
        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

        # load the page
        self.__wd.get(search_url.format(q=query))

        # Declared as a set, to prevent duplicates.
        image_urls = set()
        image_count = 0
        results_start = 0
        while image_count < max_links_to_fetch:
            self.__wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_between_interactions)

            # Get all image thumbnail results
            thumbnail_results = self.__wd.find_elements_by_css_selector("img.Q4LuWd")
            number_results = len(thumbnail_results)

            l.logI(f"Found: {number_results} search results. Extracting links from {results_start} to {number_results} url")
            if (results_start == number_results): break;

            # Loop through image thumbnail identified
            for img in thumbnail_results[results_start:number_results]:
                # Try to click every thumbnail such that we can get the real image behind it.
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception:
                    continue

                # Extract image urls
                actual_images = self.__wd.find_elements_by_css_selector("img.n3VNCb")
                for actual_image in actual_images:

                    if actual_image.get_attribute(
                        "src"
                    ) and "http" in actual_image.get_attribute("src"):
                        image_urls.add(actual_image.get_attribute("src"))

                image_count = len(image_urls)

                # If the number images found exceeds our `num_of_images`, end the seaerch.
                if len(image_urls) >= max_links_to_fetch:
                    l.logI(f"Found: {len(image_urls)} image links, done!")
                    break
            else:
                # If we haven't found all the images we want, let's look for more.
                l.logI(f"Found: {len(image_urls)} image links, looking for more...")
                time.sleep(SLEEP_BEFORE_MORE)

                # Check for button signifying no more images.
                not_what_you_want_button = ""
                try:
                    not_what_you_want_button = wd.find_element_by_css_selector(
                        ".r0zKGf")
                except:
                    pass

                # If there are no more images return.
                if not_what_you_want_button:
                    l.logI("No more images available.")
                    return None

                # If there is a "Load More" button, click it.
                load_more_button = self.__wd.find_element_by_css_selector(".mye4qd")
                if load_more_button and not not_what_you_want_button:
                    self.__wd.execute_script("document.querySelector('.mye4qd').click();")

            # Move the result startpoint further down.
            results_start = len(thumbnail_results)

        return image_urls


    ################################################################################################################################
    ### SAVE IMAGES
    def saveImage(self, folder_path: str, url: str):
        # try:
        #     l.logI("Getting image")
        #     # Download the image.  If timeout is exceeded, throw an error.
        #     with timeout(GET_IMAGE_TIMEOUT):
        #         image_content = requests.get(url).content
        # except Exception as e:
        #     l.logI(f"ERROR - Could not download {url} - {e}")

        try:
            if (self.__unverified == True): 
                image_content = requests.get(url, verify=False).content
            else:
                image_content = requests.get(url).content

            # Convert the image into a bit stream, then save it.
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGB")
            # Create a unique filepath from the contents of the image.
            file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + ".jpg")
            with open(file_path, "wb") as f:
                image.save(f, "JPEG", quality=IMAGE_QUALITY)

            # l.logI(f"SUCCESS - saved {url} - as {file_path}")
            l.logS(f"SUCCESS saved as {file_path}")
            self.__number_of_saved += 1


        except requests.exceptions.SSLError:
            l.logW(f'The certificate endpoint for {url} error occurred. Skip download.')
            pass

        except requests.exceptions.ConnectionError:
            l.logW(f'Connection to {url} return error. Skip download.')
            pass

        except UnidentifiedImageError as error:
            # l.logI(f"ERROR - Could not save {url} - {error}")
            l.logW(f"ERROR - Could not save - {error}")
            pass
        pass


    ################################################################################################################################
    ### SEARCH FOR IMAGE'S URL AND DOWNLOAD IT TO TARGET FOLDER
    def searchAndDownload(self, search_term: str, target_path="./images", 
                                number_images=5, split_to_class : bool = False):
        # Create a folder name: with path 'target_path/class/*imgs' or 'target_path/*imgs' 
        if (split_to_class == True):
            target_folder = os.path.join(target_path, "_".join(search_term.lower().split(" ")))
        else:
            target_folder = target_path

        # Create image folder if needed
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Search for images URLs
        fetched_urls = self.fetchUrls(self.__pattern, self.__number_of_images,
                        sleep_between_interactions=SLEEP_BETWEEN_INTERACTIONS)
        
        l.logI('Number of fetched URLs: ' + str(len(fetched_urls)))

        if fetched_urls is not None:
            for elem in fetched_urls:
                self.saveImage(target_folder, elem)
        else:
            l.logE(f"Failed to return links for term: {search_term}")
        pass


    def quit(self):
        self.__wd.close()
        self.__wd.quit()


    def showStatistic(self):
        l.logSym('--------------------------------------------')
        l.logI(f'Saved {self.__number_of_saved} images in {self.__output_path}')
        pass



def crawl(  webdriver, pattern, path, number_of_images, headless_mode=True, 
            unique_img_name=True,  csplit=False, unverified=False, threads = 1
         ):

    s = Searcher(   webdrv=webdriver, pattern=pattern, output_path=path, 
                    number_of_images=number_of_images, headless_mode = headless_mode, 
                    unique_img_name = unique_img_name, unverified = unverified)
        
    s.searchAndDownload( pattern, path, number_of_images)
    s.showStatistic()
    s.quit()

    pass


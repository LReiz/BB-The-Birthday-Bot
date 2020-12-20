from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import os

DRIVER_PATH = './webdriver/chromedriver_linux64/chromedriver'
FACEBOOK_CREDENTIALS_PATH = './keys/FBcredentials.json'
FABEBOOK_LOGIN_PAGE = 'https://www.facebook.com/{userId}/'

SHOW_ALL = '1'
SHOW_BIRTHDAYS_TODAY = '2'

class BirthdayCardPoster:
    def __init__(self, friendName):
        self.friendName = friendName
        self.postPageURL = ''
        self.userId = ''
        self.chromeWebdriver = None
        
        self.configChromeWebdriver(DRIVER_PATH)
        facebookCredentials = self.loadCredentials(FACEBOOK_CREDENTIALS_PATH)
        
        self.getPostPageURL()
        self.getUserId()
        self.facebookLogin(facebookCredentials['email'], facebookCredentials['password'])
        self.postBirthdayCard()
        while(True):
            continue
        

    def postBirthdayCard(self):
        self.sendImage()
        self.sendText()


    def getPostPageURL(self):
        try:
            friendInfoFile = open('./database/{}.json'.format(self.friendName))
            friendInfo = json.load(friendInfoFile)
            self.postPageURL = friendInfo['FBlink']
        except:
            print('Documento {}.json não encontrado'.format(self.friendName))


    def getUserId(self):
        userIdFirstLetterIndex = 0
        for i in range(len(self.postPageURL)-2, 0, -1):
            if self.postPageURL[i] == '/':
                userIdFirstLetterIndex = i + 1
                break
        
        self.userId = self.postPageURL[userIdFirstLetterIndex:-1]


    def configChromeWebdriver(self, webdriverPath):
        option = Options()

        option.add_argument("--disable-infobars")
        option.add_argument("start-maximized")
        option.add_argument("--disable-extensions")

        option.add_experimental_option("prefs", { 
            "profile.default_content_setting_values.notifications": 1 
        })
        self.chromeWebdriver = webdriver.Chrome(chrome_options=option, executable_path=webdriverPath)

    def facebookLogin(self, email, password):
        try:
            for i in range(2):
                self.chromeWebdriver.get(FABEBOOK_LOGIN_PAGE.format(userId=self.userId))

                self.chromeWebdriver.find_element_by_id('email').clear
                self.chromeWebdriver.find_element_by_id('email').send_keys(email)

                self.chromeWebdriver.find_element_by_id('pass').clear
                self.chromeWebdriver.find_element_by_id('pass').send_keys(password)
                self.chromeWebdriver.find_element_by_id('loginbutton').click()
                time.sleep(1)
        except:
            print("Não foi possível logar na primeira opção")
        
        try:
            self.chromeWebdriver.find_element_by_id('email').clear
            self.chromeWebdriver.find_element_by_id('email').send_keys(email)
            self.chromeWebdriver.find_element_by_id('pass').clear
            self.chromeWebdriver.find_element_by_id('pass').send_keys(password)
            self.chromeWebdriver.find_element_by_id('u_0_2').click()
        except:
            print("Não foi possível logar na segunda opção")



    def loadCredentials(self, filePath):
        jsonObject = open(filePath)
        return json.load(jsonObject)

    def sendImage(self):
        self.chromeWebdriver.get((FABEBOOK_LOGIN_PAGE+'mentions/').format(userId=self.userId))
        time.sleep(3)
        file = os.path.abspath('./temp/finalCard.png')
        try:
            self.chromeWebdriver.find_element_by_xpath("//input[@accept='image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv']").send_keys(file)
        except:
            self.chromeWebdriver.get((FABEBOOK_LOGIN_PAGE).format(userId=self.userId))
            time.sleep(3)
            self.chromeWebdriver.find_element_by_xpath("//input[@accept='image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv']").send_keys(file)

    def sendText(self):
        time.sleep(3)
        with open('./temp/finalText.json', 'rb') as file:
            finalMessage = json.load(file)['message']
        self.chromeWebdriver.find_elements_by_xpath("//div[@contenteditable='true']")[-1].send_keys(finalMessage)
        print(self.chromeWebdriver.find_elements_by_xpath("//div[@contenteditable='true']"))
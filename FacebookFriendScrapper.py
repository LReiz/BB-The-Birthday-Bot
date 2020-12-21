from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image, ImageOps, ImageDraw
import time
import requests
import io
import os
import re
import json

DRIVER_PATH = './webdriver/chromedriver_linux64/chromedriver'
FACEBOOK_CREDENTIALS_PATH = './keys/FBcredentials.json'

class FacebookFriendScrapper:
    def __init__(self):
        self.facebookURL = ''
        self.session = None
        self.friendData = {}

        self.getFriendFacebookPageURL()
        facebookCredentials = self.loadCredentials(FACEBOOK_CREDENTIALS_PATH)
        self.facebookLogin(facebookCredentials['email'], facebookCredentials['password'])
        self.getBirthdayAndName()
        self.getProfileImage()
        self.inputCharacteristics()
        self.saveFriendInDatabase()

        
    def loadCredentials(self, filePath):
        jsonObject = open(filePath)
        return json.load(jsonObject)


    def facebookLogin(self, email, password):
        facebookSession = requests.Session()
        loginPage = facebookSession.get('https://m.facebook.com/login', allow_redirects=False)
        soup = BeautifulSoup(loginPage.text, features='lxml')
        hiddenInputs = soup.find('form').findAll('input', {'type': ['hidden', 'submit']})
        post_data = {input.get('name'): input.get('value') for input in hiddenInputs}
        post_data['email'] = email
        post_data['pass'] = password
        
        facebookSession.post('https://m.facebook.com/login', data=post_data, allow_redirects=False)
        
        self.session = facebookSession
        

    def getBirthdayAndName(self):

        facebookAboutPage = self.session.get(self.facebookURL + 'about/')
        facebookAboutPageHtml = BeautifulSoup(facebookAboutPage.text, 'html.parser')

        # scrap name
        name = facebookAboutPageHtml.find('title')
        self.friendData['name'] = name.contents[0].replace(' | Facebook', '', 1)

        # scrap birthday
        birthday = facebookAboutPageHtml.findAll('td')
        for td in birthday:
            div = td.findAll('div')
            if len(div) > 0:
                birthday = re.findall(r'\d+\s\w+\s\w+\s\w+\s\d+', str(div[0]))
                if len(birthday) > 0:
                    self.friendData['birthday'] = birthday[0]

    def getProfileImage(self):
        pictureURL = self.getProfileImageURL()

        self.saveRawImageInDatabase(pictureURL)
        self.applyCircleMaskToImage()
        

    def getProfileImageURL(self):
        chromeWebdriver = webdriver.Chrome(executable_path=DRIVER_PATH)
        chromeWebdriver.get(self.facebookURL.replace("https://m", "https://www", 1))
        img = chromeWebdriver.find_element_by_class_name('profilePicThumb')
        pictureURL = img.find_element_by_tag_name('img').get_attribute('src')

        chromeWebdriver.quit()

        return pictureURL

    def saveRawImageInDatabase(self, pictureURL):
        imageContent = requests.get(pictureURL).content
        imageBytes = io.BytesIO(imageContent)
        image = Image.open(imageBytes).convert('RGBA')

        friendName = ''.join(self.friendData['name'].split(' '))
        imageFilePath = os.path.join('./database/{}.png'.format(friendName))
        with open(imageFilePath, 'wb') as file:
            image.save(file, 'PNG')

    def applyCircleMaskToImage(self):
        size = (600, 600)
        mask = Image.new('L', size, 0).convert('L')
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0) + size, fill=255)

        friendName = ''.join(self.friendData['name'].split(' '))
        image = Image.open('./database/{}.png'.format(friendName))

        output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        output.save('./database/{}.png'.format(friendName))


    def getFriendFacebookPageURL(self):
        friendFacebookPageURL = input("Insira a url da página do seu amigo(a): ")

        if friendFacebookPageURL[-1] != '/':
            friendFacebookPageURL += '/'

        self.facebookURL = friendFacebookPageURL.replace("https://www", "https://m", 1)
        self.friendData['FBlink'] = self.facebookURL
        

    def getPageHtml(pageURL):
        page = requests.get(pageURL)
        
        return BeautifulSoup(page.text, 'html.parser')


    def inputCharacteristics(self):
        friendGender = input("Com que pronomes deseja se referir ao(à) seu(sua) amigo(a) [M ou F]: ").lower()
        while friendGender != "m" and friendGender != "f":
            print("Dígito inválido. Digite 'M' ou 'F'...")
            friendGender = input("Gênero do seu(sua) amigo(a) [M ou F]: ").lower()
        
        friendCharacteristics = []
        print("Insira 5 características sobre ele(a): ")
        for i in range(5):
            friendCharacteristics.append(input("{}ª característica: ".format(i+1)))

        self.friendData['gender'] = friendGender
        self.friendData['characteristics'] = friendCharacteristics

    def saveFriendInDatabase(self):
        friendName = ''.join(self.friendData['name'].split(' '))

        with open('./database/{}.json'.format(friendName), 'w') as friendFile:
            json.dump(self.friendData, friendFile, indent=4)
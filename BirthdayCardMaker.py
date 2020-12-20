import json
import os
import random
import io
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageOps, ImageDraw
from selenium import webdriver
import requests

DRIVER_PATH = './webdriver/chromedriver_linux64/chromedriver'
IMAGE_BG_HEIGHT = 720
IMAGE_BODY_HEIGHT = 500

class BirthdayCardMaker:
    def __init__(self, friendName):
        self.friendName = friendName
        self.friendData = {}

        self.pictureData = {}
        self.bdayMessage = ''
        self.bdayPicture = './temp/bday.png'
        self.makePicture()
        self.makeText()
        pass



    def makeText(self):
        self.getFriendDataInDatabase()
        self.writeText()

    def makePicture(self):
        self.selectBackground()
        self.selectBodies()
        self.selectHeads()
        finalImage = self.assembleImage()
        self.savePicture(finalImage)

    def getFriendDataInDatabase(self):
        with open('./database/{}.json'.format(self.friendName), 'rb') as file:
            friendObject = json.load(file)
            self.friendData = friendObject

    def writeText(self):
        textModel = self.getRandomMessageModel()
        self.placeFriendCharacteristics(textModel)
        self.saveFinalText()

    def placeFriendCharacteristics(self, textModel):
        place = self.pictureData['background'].split('/')[-1]
        place = place.split('.')[0]
        firstName = self.friendData['name'].split(' ')[0]
        shuffledCharacteristics = self.friendData['characteristics'].copy()
        random.shuffle(shuffledCharacteristics)
        self.bdayMessage = textModel.format(char=shuffledCharacteristics, 
                                            name=firstName, 
                                            place=place)

    def saveFinalText(self):
        try:
            mkdir('./temp')
        except:
            print('File ./temp already exists')

        textPath = './temp/finalText.json'
        finalMessageObject = { "message": self.bdayMessage }
        with open(textPath, 'w') as file:
            json.dump(finalMessageObject, file, indent=4)

    def getRandomMessageModel(self):
        gender = self.friendData['gender']
        with open('./bday_messages/{}Messages.json'.format(gender), 'rb') as file:
            messagesObject = json.load(file)

        messagesArray = messagesObject['messages']

        return messagesArray[random.randint(0, len(messagesArray)-1)]

    def selectBackground(self):
        backgrounds = [f for f in listdir('./bday_assets/backgrounds/') if isfile(join('./bday_assets/backgrounds/', f))]
        self.pictureData['background'] = './bday_assets/backgrounds/' + backgrounds[random.randint(0, len(backgrounds)-1)]

    def selectBodies(self):
        bodies = [f for f in listdir('./bday_assets/bodies/') if isfile(join('./bday_assets/bodies/', f))]
        
        indexBodyMe = random.randint(0, len(bodies)-1)
        indexBodyFriend = random.randint(0, len(bodies)-1)
        while(indexBodyFriend == indexBodyMe):
            indexBodyFriend = random.randint(0, len(bodies)-1)

        self.pictureData['bodyMe'] = './bday_assets/bodies/' + bodies[indexBodyMe]
        self.pictureData['bodyFriend'] = './bday_assets/bodies/' + bodies[indexBodyFriend]

    def selectHeads(self):
        self.getMyHead()
        self.pictureData['headMe'] = './temp/headme.png'
        self.pictureData['headFriend'] = './database/{}.png'.format(self.friendName)

    def assembleImage(self):
        imageBg = Image.open(self.pictureData['background']).convert('RGBA')
        imageMyHead = Image.open(self.pictureData['headMe']).convert('RGBA')
        imageMyBody = Image.open(self.pictureData['bodyMe']).convert('RGBA')
        imageFriendHead = Image.open(self.pictureData['headFriend']).convert('RGBA')
        imageFriendBody = Image.open(self.pictureData['bodyFriend']).convert('RGBA')

        imageBg = self.resizeImage(imageBg, IMAGE_BG_HEIGHT)
        imageMyBody = self.resizeImage(imageMyBody, IMAGE_BODY_HEIGHT)
        imageFriendBody = self.resizeImage(imageFriendBody, IMAGE_BODY_HEIGHT)
        imageMyHead = self.resizeImage(imageMyHead, 150)
        imageFriendHead = self.resizeImage(imageFriendHead, 150)

        self.placeImageOnBackground(imageBg, imageFriendBody, 0.3)
        self.placeImageOnBackground(imageBg, imageMyBody, 0.7)
        self.placeImageOnBackground(imageBg, imageMyHead, 0.3, 0.28)
        self.placeImageOnBackground(imageBg, imageFriendHead, 0.7, 0.28)
        
        return imageBg


    def placeImageOnBackground(self, imageBg, imageBody, relativePositionX=0.3, relativePositionY = 0.45):
        
        sizeBg = imageBg.size
        sizeBody = imageBody.size

        for height in range(sizeBg[1]):
            for width in range(sizeBg[0]):
                if(width < sizeBody[0] and height < sizeBody[1] 
                    and int(width + relativePositionX*sizeBg[0]) < sizeBg[0]
                    and int(height + relativePositionY*sizeBg[1]) < sizeBg[1]
                    and int(width - (sizeBody[0]/2) + relativePositionX*sizeBg[0]) >= 0
                    and int(height + relativePositionY*sizeBg[1]) >= 0
                    and imageBody.getpixel((width, height))[3] >= 200):
                    
                    imageBg.putpixel((int(width - (sizeBody[0]/2) + (relativePositionX*sizeBg[0])), 
                                     int(height + (relativePositionY*sizeBg[1]))),
                                    imageBody.getpixel((width, height)))

    def savePicture(self, finalImage):
        try:
            os.mkdir('./temp/')
        except:
            print('File ./temp already exists')

        imageFilePath = os.path.join('./temp/finalCard.png')
        with open(imageFilePath, 'wb') as file:
            finalImage.save(file, 'PNG')


    def getMyHead(self):
        pictureURL = self.getMyImageURL()

        self.saveMyRawImageInDatabase(pictureURL)
        self.applyCircleMaskToMyImage()

    def resizeImage(self, image, newHeight):
        sizeImage = image.size
        scale = newHeight/sizeImage[1]
        newSize = (int(sizeImage[0]*scale), int(sizeImage[1]*scale))

        resizedImage = image.resize(newSize)
        return resizedImage

    def getMyImageURL(self):
        with open('./keys/FBcredentials.json', 'rb') as file:
            credentialsObject = json.load(file)
            FBlink = credentialsObject['FBlink']
        
        chromeWebdriver = webdriver.Chrome(executable_path=DRIVER_PATH)
        chromeWebdriver.get(FBlink.replace("https://m", "https://www", 1))
        img = chromeWebdriver.find_element_by_class_name('profilePicThumb')
        pictureURL = img.find_element_by_tag_name('img').get_attribute('src')

        chromeWebdriver.quit()

        return pictureURL

    def saveMyRawImageInDatabase(self, pictureURL):
        imageContent = requests.get(pictureURL).content
        imageBytes = io.BytesIO(imageContent)
        image = Image.open(imageBytes).convert('RGBA')

        try:
            os.mkdir('./temp/')
        except:
            print('File ./temp already exists')
        imageFilePath = os.path.join('./temp/headme.png')
        with open(imageFilePath, 'wb') as file:
            image.save(file, 'PNG')
    
    def applyCircleMaskToMyImage(self):
        size = (600, 600)
        mask = Image.new('L', size, 0).convert('L')
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0) + size, fill=255)

        image = Image.open('./temp/headme.png')

        output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        output.save('./temp/headme.png')
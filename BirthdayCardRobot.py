from BirthdayCardMaker import BirthdayCardMaker
from BirthdayCardPoster import BirthdayCardPoster

class BirthdayCardRobot:
    def __init__(self):
        friendName = self.getFriendName()
        BirthdayCardMaker(friendName)
        BirthdayCardPoster(friendName)

    def getFriendName(self):
        # option = input('Qual das opções a seguir?' \
        #                     '1.Mostrar todos os amigos' \
        #                     '2.Mostrar amigos que fazem aniversário hoje')
        
        # if(option == MOSTRAR_TODOS) {
            
        # } elif(option == MOSTRAR_ANIVERSARIOS_HOJE) {

        # }

        friendName = input('Nome do amigo a ser parabenizado: ')
        friendName = ''.join(friendName.split(' '))

        return friendName
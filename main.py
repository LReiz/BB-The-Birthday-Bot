from FacebookFriendScrapper import FacebookFriendScrapper
from BirthdayCardRobot import BirthdayCardRobot

OPTION_REGISTER_FRIEND = 1
OPTION_SEND_CONGRATULATIONS = 2

def chooseOption():
    option = ''
    option = input('Escolha uma das opções abaixo:\
                        \n\t1.Cadastrar um novo amigo\
                        \n\t2.Parabenizar um aniversariante\n')
    while(option != '1' and option != '2'):
        print('Insira um valor válido (entre 1 e 2)')
        option = input('Escolha uma das opções abaixo:\
                            \n\t1.Cadastrar um novo amigo\
                            \n\t2.Parabenizar um aniversariante\n')
    

    return int(option)

if __name__ == '__main__':
    option = chooseOption()
    
    if(option == OPTION_REGISTER_FRIEND):
        FacebookFriendScrapper()
    elif(option == OPTION_SEND_CONGRATULATIONS):
        BirthdayCardRobot()


import pygame
import sys
import pandas as pd
from geographiclib.geodesic import Geodesic
import datetime
import pyperclip

# function to compare two guesses
def compare(guess, mystery, df, guesses):

    # correct guess
    if mystery['Name'] == guess:

        if len(guesses) == 1:
            msg = f'You found the mystery station {guess} in 1 guess!'
        else:
            msg = f'You found the mystery station {guess} in {len(guesses)} guesses!'

        return msg, True
    
    else:
        guess = df[df['Name'] == guess].to_dict(orient = 'records')[0]

        # distance and direction
        geo = Geodesic.WGS84.Inverse(guess['Lat'], guess['Long'], mystery['Lat'], mystery['Long'])
        dist = round(geo['s12'] / 1000, 1)
        dire = ['⬆️', '↗️', '➡️', '↘️', '⬇️', '↙️', '⬅️', '↖️'][round(geo['azi1'] / 45) % 8]
        
        # patronage
        if guess['Patronage'] > mystery['Patronage']:
            patronage = '🔻'
        elif guess['Patronage'] < mystery['Patronage']:
            patronage = '🔺'
        else:
            patronage = '🟩'

        # type
        if guess['Type'] == mystery['Type']:
            typ = '🟩'
        else:
            typ = '🟥'

        # line
        if set(guess['Line']) & set(mystery['Line']):
            line = '🟩'
        elif set(guess['Group']) & set(mystery['Group']):
            line = '🟨'
        else:
            line = '🟥'

        # print comparison
        msg = f"{guess['Name']}|{dist}km|{dire}|{guess['Patronage']:,.0f}|{patronage}|{guess['Type']}|{typ}|{line}"

        return msg, False

# initialise game
pygame.init()

# setup display
width, height = 650, 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('VicRaile')
pygame.display.update()

# set fonts
titlefont = pygame.font.SysFont('segoeuiemoji', 36)
mainfont = pygame.font.SysFont('segoeuiemoji', 16)
pygame.key.set_repeat(500, 30)

# read data
df = pd.read_parquet('stationdata.parquet')

# pick mystery station
seed = int(str(datetime.date.today()).replace('-', ''))
mystery = df.sample(1, random_state = seed).to_dict(orient = 'records')[0]

# initialise game states
inputtext = ''
inputactive = True
cursortimer = 0
cursorvisible = False
guesses = []
outputtext = []
completed = False
popupmsg = None
popuptimer = 0
cols = ['Guess', 'Distance', 'Patronage', 'Type', 'Line']
pos = [30]
for w in [160, 120, 120, 120, 60][:-1]:
    pos.append(pos[-1] + w + 10)
copybutton = None
copybuttonpressed = False

# gameplay loop
while True:

    screen.fill((52, 52, 52))

    # header
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, width, 110))
    titlesurface = titlefont.render('VicRaile', True, (255, 255, 255))
    titlerect = titlesurface.get_rect(center = (width // 2, 40))
    screen.blit(titlesurface, titlerect)
    subtitlesurface = mainfont.render('Guess the Mystery Victorian Railway Station', True, (255, 255, 255))
    subtitlerect = subtitlesurface.get_rect(center = (width // 2, 85))
    screen.blit(subtitlesurface, subtitlerect)
    metrotrain = pygame.transform.scale(pygame.image.load('metrotrain.png'), (80, 80))
    screen.blit(metrotrain, (40, 15))
    vlinetrain = pygame.transform.scale(pygame.image.load('vlinetrain.png'), (80, 80))
    screen.blit(vlinetrain, (530, 15))

    for event in pygame.event.get():

        # downclick
        if event.type == pygame.MOUSEBUTTONDOWN:

            # input box
            if 20 <= event.pos[0] and event.pos[0] <= 630 and 130 <= event.pos[1] and event.pos[1] <= 165 and not completed:
                inputactive = True
            else:
                inputactive = False

            # copy button
            if completed and copybutton and copybutton.collidepoint(event.pos):
                copybuttonpressed = True

        # upclick
        elif event.type == pygame.MOUSEBUTTONUP:
            
            # copy button
            if completed and copybutton and copybutton.collidepoint(event.pos) and copybuttonpressed:

                # create text
                if len(guesses) == 1:
                    text = f'🚇 VicRaile {datetime.date.today().strftime("%d/%m/%y")} 🚇\nI found the mystery station in 1 guess!\nhttp://upcomingwebsiteurl.yippee/'
                else:
                    text = f'🚇 VicRaile {datetime.date.today().strftime("%d/%m/%y")} 🚇\nI found the mystery station in {len(guesses)} guesses!\nhttp://upcomingwebsiteurl.yippee/'

                # add to clipboard
                pyperclip.copy(text)
            
            copybuttonpressed = False

        # quit game
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # keyboard input
        elif inputactive and event.type == pygame.KEYDOWN and not completed:

            # enter to make guess
            if event.key == pygame.K_RETURN:
                
                # check if guess is a station
                if inputtext not in list(df['Name']):
                    popupmsg = f'{inputtext} is not a valid Victorian Railway Station'
                    popuptimer = pygame.time.get_ticks() + 2000

                # check if guess is not already guessed
                elif inputtext in guesses:
                    popupmsg = 'You have already guessed this station'
                    popuptimer = pygame.time.get_ticks() + 2000
                
                # valid guess
                else:
                    guesses.append(inputtext)
                    msg, result = compare(inputtext, mystery, df, guesses)
                    outputtext.append(msg)

                    # check for correct guess
                    if result:
                        completed = True
                
                # reset input text
                inputtext = ''

            # backspace
            elif event.key == pygame.K_BACKSPACE:
                inputtext = inputtext[:-1]

            # other keys add to input
            else:
                inputtext += event.unicode

    # render input box
    pygame.draw.rect(screen, (70, 70, 70), (20, 130, 610, 35), border_radius = 5)
    inputsurface = mainfont.render(f'Guess: {inputtext}', True, (255, 255, 255))
    screen.blit(inputsurface, (30, 141))

    # blinking cursor
    if inputactive and cursorvisible and not completed:
        pygame.draw.line(screen, (255, 255, 255), (31 + inputsurface.get_width(), 139), (31 + inputsurface.get_width(), 155), 2)
    if pygame.time.get_ticks() - cursortimer > 500:
        cursorvisible = not cursorvisible
        cursortimer = pygame.time.get_ticks()

    # popup for error inputs
    if popupmsg and pygame.time.get_ticks() < popuptimer:
        popupsurface = mainfont.render(popupmsg, True, (255, 80, 80))
        screen.blit(popupsurface, ((width // 2) - popupsurface.get_width() // 2, 141))

    # render output table header
    if outputtext and '|' in outputtext[0]:
        for i, col in enumerate(cols):
            tableheader = mainfont.render(col, True, (255, 255, 255))
            screen.blit(tableheader, (pos[i], 190))
        pygame.draw.line(screen, (255, 255, 255), (30, 210), (620, 210), 1)

    # render output table lines
    for i, line in enumerate(outputtext):
        h = 220 + i * 35

        # wrong guess information
        if '|' in line:
            split = line.split('|')
            name = split[0]
            distance = split[1]
            direction = split[2]
            patronage = split[3]
            patronageemoji = split[4]
            typ = split[5]
            typemoji = split[6]
            line = split[7]

            # name
            screen.blit(mainfont.render(name, True, (255, 255, 255)), (pos[0], h))

            # distance/direction
            screen.blit(mainfont.render(distance.strip(), True, (255, 255, 255)), (pos[1], h))
            screen.blit(mainfont.render(direction.strip(), True, (255, 255, 255)), (pos[1] + 70, h))

            # patronage
            screen.blit(mainfont.render(patronage.strip(), True, (255, 255, 255)), (pos[2], h))
            screen.blit(mainfont.render(patronageemoji.strip(), True, (255, 255, 255)), (pos[2] + 90, h))

            # type
            screen.blit(mainfont.render(typ.strip(), True, (255, 255, 255)), (pos[3], h))
            screen.blit(mainfont.render(typemoji.strip(), True, (255, 255, 255)), (pos[3] + 90, h))

            # line
            screen.blit(mainfont.render(line.strip(), True, (255, 255, 255)), (pos[4] + 5, h))

        # win message
        else:
            
            if len(guesses) == 1:
                h = h - 30

            victorysurface = mainfont.render(line, True, (100, 255, 100))
            screen.blit(victorysurface, ((width // 2) - victorysurface.get_width() // 2, h))
            
            # copy button
            copybutton = pygame.Rect(width // 2 - 50, h + 30, 100, 40)
            if copybuttonpressed:
                copybuttoncolour = (70, 100, 70)
            else:
                copybuttoncolour = (80, 120, 80)
            pygame.draw.rect(screen, copybuttoncolour, copybutton, border_radius = 0)
            buttonsurface = mainfont.render('Copy', True, (255, 255, 255))
            screen.blit(buttonsurface, buttonsurface.get_rect(center = copybutton.center))

    pygame.display.flip()

import pygame
import sys
import json
import random
import math
import datetime
import asyncio
import js

# function to copy text to clipboard
def copyclipboard(text):
    
    # use browser js
    promise = js.navigator.clipboard.writeText(text)
    promise.then(lambda _: print("Text copied to clipboard!")).catch(lambda err: print("Error:", err))

# function to calculate distance and direction between two sets of geographic coordinates
def distdire(lat1, lon1, lat2, lon2):
    
    # convert to radians
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # distance using haversine formula
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    angle = math.sin(dlat / 2)**2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2)**2
    distance = 6371 * 2 * math.atan2(math.sqrt(angle), math.sqrt(1 - angle))

    # bearing
    x = math.sin(dlon) * math.cos(rlat2)
    y = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlon)
    direction = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'][round((math.degrees(math.atan2(x, y)) + 360) % 360 / 45) % 8]

    return distance, direction

# function to compare two guesses
def compare(guess, mystery, data, guesses):

    # correct guess
    if mystery['Name'] == guess:

        if len(guesses) == 1:
            msg = f'You found the mystery station {guess} in 1 guess!'
        else:
            msg = f'You found the mystery station {guess} in {len(guesses)} guesses!'

        return {'win': msg}, True
    
    else:
        guess = [i for i in data if i['Name'] == guess][0]

        # distance and direction
        distance, direction = distdire(guess['Lat'], guess['Long'], mystery['Lat'], mystery['Long'])
        
        # patronage
        if guess['Patronage'] > mystery['Patronage']:
            patronageemoji = 'down'
        elif guess['Patronage'] < mystery['Patronage']:
            patronageemoji = 'up'
        else:
            patronageemoji = 'equals'

        # type
        if guess['Type'] == mystery['Type']:
            typeemoji = 'green'
        else:
            typeemoji = 'red'

        # line
        if set(guess['Line']) & set(mystery['Line']):
            line = 'green'
        elif set(guess['Group']) & set(mystery['Group']):
            line = 'yellow'
        else:
            line = 'red'

        # return result
        result = {
            'name': guess['Name'], 
            'distance': f'{distance:.1f}km', 
            'direction': direction, 
            'patronage': f'{guess["Patronage"]:,.0f}', 
            'patronageemoji': patronageemoji, 
            'type': guess['Type'], 
            'typeemoji': typeemoji, 
            'line': line
        }

        return result, False

async def main():

    # initialise game
    pygame.init()

    # setup display
    width, height = 650, 1000
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('VicRaile')
    pygame.display.update()

    # set fonts
    titlefont = pygame.font.Font('./assets/scriptbl.ttf', 40)
    mainfont = pygame.font.Font('./assets/segoeui.ttf', 16)
    pygame.key.set_repeat(500, 30)

    # read data
    with open('stationdata.json', 'r') as f:
        data = json.load(f)

    # pick mystery station
    random.seed(int(str(datetime.date.today()).replace('-', '')))
    mystery = random.choice(data)

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
    pos = [30]
    for w in [160, 100, 120, 120, 60][:-1]:
        pos.append(pos[-1] + w + 10)
    enterbutton = None
    enterbuttonpressed = False
    copybutton = None
    copybuttonpressed = False

    # load emoji images
    emojis = {
        'n': pygame.image.load('./assets/n.png').convert_alpha(), 
        'ne': pygame.image.load('./assets/ne.png').convert_alpha(), 
        'e': pygame.image.load('./assets/e.png').convert_alpha(), 
        'se': pygame.image.load('./assets/se.png').convert_alpha(), 
        's': pygame.image.load('./assets/s.png').convert_alpha(), 
        'sw': pygame.image.load('./assets/sw.png').convert_alpha(), 
        'w': pygame.image.load('./assets/w.png').convert_alpha(), 
        'nw': pygame.image.load('./assets/nw.png').convert_alpha(), 
        'up': pygame.image.load('./assets/up.png').convert_alpha(), 
        'down': pygame.image.load('./assets/down.png').convert_alpha(), 
        'equals': pygame.image.load('./assets/equals.png').convert_alpha(), 
        'red': pygame.image.load('./assets/red.png').convert_alpha(), 
        'yellow': pygame.image.load('./assets/yellow.png').convert_alpha(), 
        'green': pygame.image.load('./assets/green.png').convert_alpha()
    }
    for key in emojis:
        emojis[key] = pygame.transform.scale(emojis[key], (24, 24))

    # gameplay loop
    while True:

        # visuals
        screen.fill((52, 52, 52))

        # header
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, width, 110))
        titlesurface = titlefont.render('VicRaile', True, (255, 255, 255))
        titlerect = titlesurface.get_rect(center = (width // 2, 40))
        screen.blit(titlesurface, titlerect)
        subtitlesurface = mainfont.render('Guess the Mystery Victorian Railway Station', True, (255, 255, 255))
        subtitlerect = subtitlesurface.get_rect(center = (width // 2, 85))
        screen.blit(subtitlesurface, subtitlerect)
        metrotrain = pygame.transform.scale(pygame.image.load('./assets/metro.png'), (80, 80))
        screen.blit(metrotrain, (40, 15))
        vlinetrain = pygame.transform.scale(pygame.image.load('./assets/vline.png'), (80, 80))
        screen.blit(vlinetrain, (530, 15))

        # enter button
        enterbutton = pygame.Rect(530, 130, 100, 35)
        if enterbuttonpressed:
            enterbuttoncolour = (110, 110, 110)
        else:
            enterbuttoncolour = (90, 90, 90)
        pygame.draw.rect(screen, enterbuttoncolour, enterbutton, border_radius = 5)
        enterbuttonsurface = mainfont.render('Enter', True, (255, 255, 255))
        screen.blit(enterbuttonsurface, enterbuttonsurface.get_rect(center = (enterbutton.centerx, enterbutton.centery)))

        # input detection
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

                # enter button
                if enterbutton.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
                    enterbuttonpressed = True

            # upclick
            elif event.type == pygame.MOUSEBUTTONUP:
                
                # copy button
                if completed and copybutton and copybutton.collidepoint(event.pos) and copybuttonpressed:

                    # create text
                    if len(guesses) == 1:
                        text = f'VicRaile {datetime.date.today().strftime("%d/%m/%y")}\nI found the mystery station in 1 guess!\nhttp://upcomingwebsiteurl.yippee/'
                    else:
                        text = f'VicRaile {datetime.date.today().strftime("%d/%m/%y")}\nI found the mystery station in {len(guesses)} guesses!\nhttp://upcomingwebsiteurl.yippee/'

                    # add to clipboard
                    copyclipboard(text)
                
                copybuttonpressed = False
                
                # enter button
                enterbuttonpressed = False

            # quit game
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keyboard input
            elif inputactive and event.type == pygame.KEYDOWN and not completed:

                # enter to make guess
                if event.key == pygame.K_RETURN:
                        
                    # blank input
                    if inputtext != '':
                    
                        # check if guess is a station
                        if inputtext not in [list(i.values())[0] for i in data]:
                            popupmsg = f'{inputtext} is not a valid Victorian Railway Station'
                            popuptimer = pygame.time.get_ticks() + 2000

                        # check if guess is not already guessed
                        elif inputtext in guesses:
                            popupmsg = 'You have already guessed this station'
                            popuptimer = pygame.time.get_ticks() + 2000
                        
                        # valid guess
                        else:
                            guesses.append(inputtext)
                            dict, correct = compare(inputtext, mystery, data, guesses)
                            outputtext.append(dict)

                            # check for correct guess
                            if correct:
                                completed = True
                        
                        # reset input text
                        inputtext = ''

                # backspace
                elif event.key == pygame.K_BACKSPACE:
                    inputtext = inputtext[:-1]

                # other keys add to input
                else:
                    inputtext += event.unicode

        # input box with placeholder text and blinking cursor
        pygame.draw.rect(screen, (90, 90, 90), (20, 130, 490, 35), border_radius = 5)
        if inputtext == '':
            guesssurface = mainfont.render('Guess:', True, (255, 255, 255))
            screen.blit(guesssurface, (30, 136))
            if inputactive and cursorvisible and not completed:
                pygame.draw.line(screen, (255, 255, 255), (30, 139), (30, 155), 2)
        else:
            inputsurface = mainfont.render(f'{inputtext}', True, (255, 255, 255))
            screen.blit(inputsurface, (30, 136))
            if inputactive and cursorvisible and not completed:
                pygame.draw.line(screen, (255, 255, 255), (31 + inputsurface.get_width(), 139), (31 + inputsurface.get_width(), 155), 2)
        if pygame.time.get_ticks() - cursortimer > 500:
            cursorvisible = not cursorvisible
            cursortimer = pygame.time.get_ticks()

        # popup for error inputs
        if popupmsg and pygame.time.get_ticks() < popuptimer:
            popupsurface = mainfont.render(popupmsg, True, (255, 80, 80))
            screen.blit(popupsurface, (270 - popupsurface.get_width() // 2, 141))

        # output table header
        if outputtext and not 'win' in outputtext[0]:
            for i, col in enumerate(['Guess', 'Distance', 'Patronage', 'Type', 'Line']):
                tableheader = mainfont.render(col, True, (255, 255, 255))
                screen.blit(tableheader, (pos[i], 170))
            pygame.draw.line(screen, (255, 255, 255), (30, 200), (620, 200), 1)

        # output table lines
        for i, result in enumerate(outputtext):
            h = 205 + i * 30

            # wrong guess information
            if 'win' not in result:

                # name
                screen.blit(mainfont.render(result['name'], True, (255, 255, 255)), (pos[0], h))

                # distance/direction
                screen.blit(mainfont.render(result['distance'], True, (255, 255, 255)), (pos[1], h))
                screen.blit(emojis[result['direction']], (pos[1] + 70, h))

                # patronage
                screen.blit(mainfont.render(result['patronage'], True, (255, 255, 255)), (pos[2], h))
                screen.blit(emojis[result['patronageemoji']], (pos[2] + 90, h))

                # type
                screen.blit(mainfont.render(result['type'], True, (255, 255, 255)), (pos[3], h))
                screen.blit(emojis[result['typeemoji']], (pos[3] + 90, h))

                # line
                screen.blit(emojis[result['line']], (pos[4], h))

            # win message
            else:
                
                if len(guesses) == 1:
                    h = h - 25

                victorysurface = mainfont.render(result['win'], True, (100, 255, 100))
                screen.blit(victorysurface, ((width // 2) - victorysurface.get_width() // 2, h))
                
                # copy button
                copybutton = pygame.Rect(width // 2 - 50, h + 35, 100, 40)
                if copybuttonpressed:
                    copybuttoncolour = (70, 100, 70)
                else:
                    copybuttoncolour = (80, 120, 80)
                pygame.draw.rect(screen, copybuttoncolour, copybutton, border_radius = 5)
                buttonsurface = mainfont.render('Copy', True, (255, 255, 255))
                screen.blit(buttonsurface, buttonsurface.get_rect(center = copybutton.center))

        pygame.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())
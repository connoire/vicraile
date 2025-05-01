import pygame
import sys
import json
import random
import math
import datetime
import asyncio

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
            typeemoji = 'tick'
        else:
            typeemoji = 'cross'

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
    clock = pygame.time.Clock()

    # setup display
    width, height = 650, 900
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('VicRaile')
    icon = pygame.image.load('./train.png')
    pygame.display.set_icon(icon)
    pygame.display.update()

    # set fonts
    titlefont = pygame.font.Font('./assets/scriptbl.ttf', 40)
    mainfont = pygame.font.Font('./assets/segoeui.ttf', 16)
    pygame.key.set_repeat(500, 30)

    # read data
    with open('stationdata.json', 'r') as f:
        data = json.load(f)

    # initialise game states
    inputtext = ''
    inputactive = False
    cursortimer = 0
    cursorvisible = False
    guesses = []
    outputtext = []
    completed = False
    popupmsg = None
    popuptimer = 0
    pos = [30]
    for w in [170, 100, 120, 120, 60][:-1]:
        pos.append(pos[-1] + w + 10)
    modechosen = False
    dailybutton = None
    dailybuttonpressed = False
    randombutton = None
    randombuttonpressed = False
    enterbutton = None
    enterbuttonpressed = False
    copybutton = None
    copybuttonpressed = False
    playagainbutton = None
    playagainbuttonpressed = False

    # colours
    white = (255, 255, 255)
    grey = (52, 52, 52)
    greylight = (90, 90, 90)
    greydark = (35, 35, 35)
    greylightdark = (70, 70, 70)
    red = (255, 90, 90)
    green = (100, 180, 100)
    greendark = (80, 160, 80)

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
        'tick': pygame.image.load('./assets/tick.png').convert_alpha(), 
        'cross': pygame.image.load('./assets/cross.png').convert_alpha(), 
        'red': pygame.image.load('./assets/red.png').convert_alpha(), 
        'yellow': pygame.image.load('./assets/yellow.png').convert_alpha(), 
        'green': pygame.image.load('./assets/green.png').convert_alpha()
    }
    for key in emojis:
        emojis[key] = pygame.transform.scale(emojis[key], (24, 24))

    # gameplay loop
    while True:

        # background
        screen.fill(grey)

        # header
        pygame.draw.rect(screen, greydark, (0, 0, width, 110))
        titlesurface = titlefont.render('VicRaile', True, white)
        titlerect = titlesurface.get_rect(center = (width // 2, 40))
        screen.blit(titlesurface, titlerect)
        subtitlesurface = mainfont.render('Guess the Mystery Victorian Railway Station', True, white)
        subtitlerect = subtitlesurface.get_rect(center = (width // 2, 85))
        screen.blit(subtitlesurface, subtitlerect)
        metrotrain = pygame.transform.scale(pygame.image.load('./assets/metro.png'), (80, 80))
        screen.blit(metrotrain, (60, 15))
        vlinetrain = pygame.transform.scale(pygame.image.load('./assets/vline.png'), (80, 80))
        screen.blit(vlinetrain, (510, 15))

        # input detection
        for event in pygame.event.get():

            # downclick
            if event.type == pygame.MOUSEBUTTONDOWN:

                # daily button
                if not modechosen and dailybutton and dailybutton.collidepoint(event.pos):
                    dailybuttonpressed = True
                
                # random button
                if not modechosen and randombutton and randombutton.collidepoint(event.pos):
                    randombuttonpressed = True

                # input box
                if 20 <= event.pos[0] and event.pos[0] <= 630 and 130 <= event.pos[1] and event.pos[1] <= 165 and not completed:
                    inputactive = True
                else:
                    inputactive = False

                # copy button
                if completed and copybutton and copybutton.collidepoint(event.pos):
                    copybuttonpressed = True

                # enter button
                if enterbutton and enterbutton.collidepoint(event.pos):
                    enterbuttonpressed = True

                # play again button
                if completed and playagainbutton and playagainbutton.collidepoint(event.pos):
                    playagainbuttonpressed = True

            # upclick
            elif event.type == pygame.MOUSEBUTTONUP:
                
                # daily button
                if not modechosen and dailybutton and dailybutton.collidepoint(event.pos) and dailybuttonpressed:
                    
                    # pick mystery
                    random.seed(int(str(datetime.date.today()).replace('-', '')))
                    mystery = random.choice(data)

                    modechosen = 'daily'
                    dailybutton = None
                    randombutton = None
                    inputactive = True
                
                # random button
                if not modechosen and randombutton and randombutton.collidepoint(event.pos) and randombuttonpressed:

                    # pick mystery
                    random.seed()
                    mystery = random.choice(data)

                    modechosen = 'random'
                    dailybutton = None
                    randombutton = None
                    inputactive = True

                # copy button
                if completed and copybutton and copybutton.collidepoint(event.pos) and copybuttonpressed:

                    # create text
                    if len(guesses) == 1:
                        text = f'VicRaile {datetime.date.today().strftime("%d/%m/%y")}\nI found the mystery station in 1 guess!\nhttps://connoire.github.io/vicraile/'
                    else:
                        text = f'VicRaile {datetime.date.today().strftime("%d/%m/%y")}\nI found the mystery station in {len(guesses)} guesses!\nhttps://connoire.github.io/vicraile/'

                    # add to clipboard
                    try:

                        # use js in browser
                        import js
                        js.navigator.clipboard.writeText(text)

                    except:

                        # use pyperclip in desktop
                        import pyperclip
                        pyperclip.copy(text)

                # enter button
                if enterbutton and enterbutton.collidepoint(event.pos) and enterbuttonpressed:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))

                # play again button
                if completed and playagainbutton and playagainbutton.collidepoint(event.pos) and playagainbuttonpressed:
                    
                    # reinitialise game states
                    inputtext = ''
                    inputactive = False
                    cursortimer = 0
                    cursorvisible = False
                    guesses = []
                    outputtext = []
                    completed = False
                    popupmsg = None
                    popuptimer = 0
                    pos = [30]
                    for w in [170, 100, 120, 120, 60][:-1]:
                        pos.append(pos[-1] + w + 10)
                    modechosen = False
                    dailybutton = None
                    dailybuttonpressed = False
                    randombutton = None
                    randombuttonpressed = False
                    enterbutton = None
                    enterbuttonpressed = False
                    copybutton = None
                    copybuttonpressed = False
                    playagainbutton = None
                    playagainbuttonpressed = False
            
                # unclick buttons
                dailybuttonpressed = False
                randombuttonpressed = False
                copybuttonpressed = False
                enterbuttonpressed = False
                playagainbuttonpressed = False

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
                        if inputtext.lower() not in [list(i.values())[0].lower() for i in data]:
                            popupmsg = f'Not a valid Victorian Railway Station'
                            popuptimer = pygame.time.get_ticks() + 2000

                        # check if guess is not already guessed
                        elif inputtext.lower() in [i.lower() for i in guesses]:
                            popupmsg = 'You have already guessed this station'
                            popuptimer = pygame.time.get_ticks() + 2000
                        
                        # valid guess
                        else:

                            # correct capitalisation
                            guess = next(list(i.values())[0] for i in data if list(i.values())[0].lower() == inputtext.lower())
                            guesses.append(guess)

                            # compare guess
                            dict, correct = compare(guess, mystery, data, guesses)
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

                    # check if key will make text too long
                    if mainfont.size(inputtext + event.unicode)[0] < 470:
                        inputtext += event.unicode

        # gamemode choice buttons
        if not modechosen:

            # daily button
            dailybutton = pygame.Rect(175, 130, 100, 35)
            if dailybuttonpressed:
                dailybuttoncolour = greylightdark
            else:
                dailybuttoncolour = greylight
            pygame.draw.rect(screen, dailybuttoncolour, dailybutton, border_radius = 5)
            dailybuttonsurface = mainfont.render('Daily', True, white)
            screen.blit(dailybuttonsurface, dailybuttonsurface.get_rect(center = (dailybutton.centerx, dailybutton.centery)))

            # random button
            randombutton = pygame.Rect(375, 130, 100, 35)
            if randombuttonpressed:
                dailybuttoncolour = greylightdark
            else:
                randombuttoncolour = greylight
            pygame.draw.rect(screen, randombuttoncolour, randombutton, border_radius = 5)
            randombuttonsurface = mainfont.render('Random', True, white)
            screen.blit(randombuttonsurface, randombuttonsurface.get_rect(center = (randombutton.centerx, randombutton.centery)))

        # player input line
        if modechosen:

            # input box with placeholder text and blinking cursor
            pygame.draw.rect(screen, greylight, (20, 130, 490, 35), border_radius = 5)
            if inputtext == '':
                guesssurface = mainfont.render('Guess:', True, white)
                screen.blit(guesssurface, (30, 136))
                if inputactive and cursorvisible and not completed:
                    pygame.draw.line(screen, white, (30, 139), (30, 155), 2)
            else:
                inputsurface = mainfont.render(f'{inputtext}', True, white)
                screen.blit(inputsurface, (30, 136))
                if inputactive and cursorvisible and not completed:
                    pygame.draw.line(screen, white, (31 + inputsurface.get_width(), 139), (31 + inputsurface.get_width(), 155), 2)
            if pygame.time.get_ticks() - cursortimer > 500:
                cursorvisible = not cursorvisible
                cursortimer = pygame.time.get_ticks()

            # enter button
            enterbutton = pygame.Rect(530, 130, 100, 35)
            if enterbuttonpressed:
                enterbuttoncolour = greylightdark
            else:
                enterbuttoncolour = greylight
            pygame.draw.rect(screen, enterbuttoncolour, enterbutton, border_radius = 5)
            enterbuttonsurface = mainfont.render('Enter', True, white)
            screen.blit(enterbuttonsurface, enterbuttonsurface.get_rect(center = (enterbutton.centerx, enterbutton.centery)))

        # error input popup
        if popupmsg and pygame.time.get_ticks() < popuptimer:
            popupsurface = mainfont.render(popupmsg, True, red)
            screen.blit(popupsurface, ((width - popupsurface.get_width()) // 2, 136))

        # output table header
        if outputtext and not 'win' in outputtext[0]:
            for i, col in enumerate(['Name', 'Distance', 'Patronage', 'Type', 'Line']):
                tableheader = mainfont.render(col, True, white)
                screen.blit(tableheader, (pos[i], 180))
            pygame.draw.line(screen, white, (20, 210), (630, 210), 1)

        # output table lines
        for i, result in enumerate(outputtext):
            h = 215 + i * 30

            # wrong guess information
            if 'win' not in result:

                # name
                screen.blit(mainfont.render(result['name'], True, white), (pos[0], h))

                # distance/direction
                screen.blit(mainfont.render(result['distance'], True, white), (pos[1], h))
                screen.blit(emojis[result['direction']], (pos[1] + 70, h))

                # patronage
                screen.blit(mainfont.render(result['patronage'], True, white), (pos[2], h))
                screen.blit(emojis[result['patronageemoji']], (pos[2] + 90, h))

                # type
                screen.blit(mainfont.render(result['type'], True, white), (pos[3], h))
                screen.blit(emojis[result['typeemoji']], (pos[3] + 90, h))

                # line
                screen.blit(emojis[result['line']], (pos[4] + 3, h))

            # win message
            else:
                
                if len(guesses) == 1:
                    h = h - 30

                victorysurface = mainfont.render(result['win'], True, green)
                screen.blit(victorysurface, ((width // 2) - victorysurface.get_width() // 2, h + 5))
                
                # copy button
                if modechosen == 'daily':
                    copybutton = pygame.Rect(width // 2 - 50, h + 95, 100, 40)
                    if copybuttonpressed:
                        copybuttoncolour = greendark
                    else:
                        copybuttoncolour = green
                    pygame.draw.rect(screen, copybuttoncolour, copybutton, border_radius = 5)
                    copybuttonsurface = mainfont.render('Copy', True, white)
                    screen.blit(copybuttonsurface, copybuttonsurface.get_rect(centerx = copybutton.centerx, centery = copybutton.centery - 2))

                # play again button
                playagainbutton = pygame.Rect(width // 2 - 50, h + 40, 100, 40)
                if playagainbuttonpressed:
                    playagainbuttoncolour = greendark
                else:
                    playagainbuttoncolour = green
                pygame.draw.rect(screen, playagainbuttoncolour, playagainbutton, border_radius = 5)
                playagainbuttonsurface = mainfont.render('Play Again', True, white)
                screen.blit(playagainbuttonsurface, playagainbuttonsurface.get_rect(centerx = playagainbutton.centerx, centery = playagainbutton.centery - 2))

        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
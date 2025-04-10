import pandas as pd
from geographiclib.geodesic import Geodesic
import datetime

import pygame
import sys

def compare(guess, mystery, df, guesses):

    # correct guess
    if mystery['Name'] == guess:
        msg = f'You got the correct station {guess} in {len(guesses)} guesses!'
        return msg, True
    
    else:
        guess = df[df['Name'] == guess].to_dict(orient = 'records')[0]

        # distance and direction
        geo = Geodesic.WGS84.Inverse(guess['Lat'], guess['Long'], mystery['Lat'], mystery['Long'])
        dist = round(geo['s12'] / 1000, 1)
        dire = ['⬆️', '↗️', '➡️', '↘️', '⬇️', '↙️', '⬅️', '↖️'][round(geo['azi1'] / 45) % 8]
        
        # patronage
        if guess['Patronage'] > mystery['Patronage']:
            patronage = '⬇️'
        elif guess['Patronage'] < mystery['Patronage']:
            patronage = '⬆️'
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
        msg = f"{guess['Name']} | Distance: {dist}km {dire} | Patronage: {guess['Patronage']:,.0f} {patronage} | Type: {guess['Type']} {typ} | Line: {line}"

        return msg, False

# initialise game
pygame.init()
pygame.key.set_repeat(300, 30)
font = pygame.font.SysFont('segoeuiemoji', 16)

# setup display
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('VicRaile')
pygame.display.update()

# read data
df = pd.read_parquet('stationdata.parquet')

# pick mystery station
seed = int(str(datetime.date.today()).replace('-', ''))
mystery = df.sample(1, random_state = seed).to_dict(orient = 'records')[0]

# game state
inputtext = ''
guesses = []
outputtext = []
running = True
completed = False

# gameplay loop
while running:
    screen.fill((52, 52, 52))

    for event in pygame.event.get():

        # quit game
        if event.type == pygame.QUIT:
            running = False

        # keyboard input
        elif event.type == pygame.KEYDOWN and not completed:

            # enter to make guess
            if event.key == pygame.K_RETURN:
                
                # check if guess is a station
                if inputtext not in list(df['Name']):
                    outputtext.append(f'{inputtext} is not a valid Victorian railway station')

                # check if guess is not already guessed
                elif inputtext in guesses:
                    outputtext.append('You have already guessed this station')
                
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

            # alphabetic key adds to input
            else:
                inputtext += event.unicode
    
    # render input box
    inputbox = font.render(f'Guess Station: {inputtext}', True, (255, 255, 255))
    screen.blit(inputbox, (30, 20))

    # render output
    for i, line in enumerate(outputtext):
        output_surface = font.render(line, True, (255, 255, 255))
        screen.blit(output_surface, (30, 60 + i * 40))

    pygame.display.flip()

pygame.quit()
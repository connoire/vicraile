import pandas as pd
from geographiclib.geodesic import Geodesic
import datetime

def compare(guess, mystery, df):

    # first guess
    if not guess:
        return

    # correct guess
    if mystery['Name'] == guess:
        return True
    
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
        print(f"Name: {guess['Name']}\t\tDistance: {dist}km {dire}\t\tPatronage: {guess['Patronage']:,.0f} {patronage}\t\tType: {guess['Type']} {typ}\t\tLine: {line}")

        return False

def play(mode):

    # read data
    df = pd.read_parquet('stationdata.parquet')

    # pick mystery station
    if mode == 'random':
        mystery = df.sample(1).to_dict(orient = 'records')[0]
    
    elif mode == 'daily':
        seed = int(str(datetime.date.today()).replace('-', ''))
        mystery = df.sample(1, random_state = seed).to_dict(orient = 'records')[0]

    guess = None
    guesses = []

    # keep guessing unti mystery is guessed
    while not compare(guess, mystery, df):

        while True:
            guess = input('Guess: ')

            # check if guess is a station
            if guess not in list(df['Name']):
                print(f'{guess} is not a valid Victorian railway station')

            # check if guess is not already guessed
            elif guess in guesses:
                print('You have already guessed this station')

            # valid guess
            else:
                guesses.append(guess)
                break

    # correct guess
    print(f'You got the correct station {guess} in {len(guesses)} guesses!')

play('daily')
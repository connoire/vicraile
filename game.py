import pandas as pd
from geographiclib.geodesic import Geodesic

def compare(guess, mystery, df):

    # first guess
    if not guess:
        return

    # correct guess
    if mystery['Name'] == guess:
        return True
    
    else:
        guess = df[df['Name'] == guess].to_dict(orient = 'records')[0]

        # distance/direction
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
        print(f'Name: {guess['Name']}    Distance: {dist} {dire}    Patronage: {guess['Patronage']} {patronage}    Type: {guess['Type']} {typ}    Line: {line}')

        return False

def play():

    # read data
    df = pd.read_parquet('stationdata.parquet')

    # pick mystery station
    mystery = df.sample(1).to_dict(orient = 'records')[0]

    guess = None
    attempts = 0

    # keep guessing unti mystery is guessed
    while not compare(guess, mystery, df):

        # check if guess is a station
        while True:
            guess = input('Guess: ')

            if guess not in list(df['Name']):
                print(f'{guess} is not a valid Victorian railway station')

            else:
                attempts += 1
                break

    # correct guess
    print(f'You got the correct station {guess} in {attempts} guesses!')

play()
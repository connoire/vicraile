import pandas as pd

def compare(mystery, guess, df):

    if not guess:
        return

    # correct guess
    if mystery['Name'] == guess:
        return True
    
    else:
        guess = df[df['Name'] == guess].to_dict(orient = 'records')[0]

        # distance/direction
        


        return False

def play():

    # read data
    df = pd.read_parquet('stationdata.parquet')

    # pick mystery station
    mystery = df.sample(1).to_dict(orient = 'records')[0]

    guess = None
    attempts = 0

    # keep guessing unti mystery is guessed
    while not compare(mystery, guess, df):

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
import requests

def download(url, path):
    req = requests.get(url)
    with open(path, 'wb') as f:
        f.write(req.content)

if __name__ == '__main__':

    download('https://opendata.transport.vic.gov.au/dataset/2fa2cdfa-84f1-455e-b6c9-058b92774b34/resource/57faf356-36a3-4bbe-87fe-f0f05d1b8996/download/annual_metropolitan_train_station_entries_fy_2023_2024.csv', './annual_metropolitan_train_station_entries_fy_2023_2024.csv')
    download('https://opendata.transport.vic.gov.au/dataset/2d4f81dc-f56a-4bcf-8291-ee04fe9669e6/resource/f93a819a-351e-4242-a6f3-74d92cd682dc/download/annual_regional_train_station_entries_fy_2023_2024.csv', './annual_regional_train_station_entries_fy_2023_2024.csv')
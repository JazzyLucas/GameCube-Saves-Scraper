import os
import requests
from bs4 import BeautifulSoup
import zipfile

base_url = 'https://gc-saves.com'

save_dir = 'gc_saves'
os.makedirs(save_dir, exist_ok=True)


def fetch_page(url):
    print(f'Fetching page: {url}')
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return BeautifulSoup(response.text, 'html.parser')


def download_file(url, path):
    print(f'Downloading save file: {url}')
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    with open(path, 'wb') as file:
        file.write(response.content)
    print(f'Downloaded {path}')


try:
    main_soup = fetch_page(base_url)
except requests.exceptions.RequestException as e:
    print(f'Error fetching main page: {e}')
    exit(1)

# Find all game container links
game_links = main_soup.find_all('a', href=lambda href: href and '/game/' in href)
print(f'Found {len(game_links)} game container links.')

# Download each save file into the same folder
for index, game_link in enumerate(game_links, start=1):
    game_url = base_url + game_link['href']
    print(f'\nProcessing game container: {game_url}')

    try:
        game_soup = fetch_page(game_url)
    except requests.exceptions.RequestException as e:
        print(f'Error fetching game container page: {e}')
        continue

    # Find the link to the save file
    save_file_link = game_soup.find('a', href=lambda href: href and href.endswith('.gci'))

    if save_file_link:
        save_file_url = base_url + save_file_link['href']
        save_file_name = os.path.basename(save_file_url)
        file_path = os.path.join(save_dir, save_file_name)

        if not os.path.exists(file_path):
            try:
                download_file(save_file_url, file_path)
            except requests.exceptions.RequestException as e:
                print(f'Error downloading save file: {e}')
        else:
            print(f'Save file already exists: {file_path}')
    else:
        print(f'No save file found on page: {game_url}')

# Create a zip file of the downloaded save files
zip_file_path = 'gc_saves.zip'
print(f'Creating zip file: {zip_file_path}')
with zipfile.ZipFile(zip_file_path, 'w') as zipf:
    for root, dirs, files in os.walk(save_dir):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, save_dir))

print(f'All files downloaded and zipped into {zip_file_path}.')

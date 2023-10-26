"""This module contains a few useful functions to handle all sorts of ripcomic's commands."""
import outputformat, subprocess

from bs4 import BeautifulSoup
from ripcomic import BASE_SEARCH_URL, SESSION, DEBUG

### HELPERS
def download_comic(comic_url: str, title: str, path: str):
    """Downloads the comic onto the file system"""
    comic_page_parser = BeautifulSoup(SESSION.get(comic_url, timeout=15).text, 'html.parser')

    try:
        download_url = comic_page_parser.find('a', class_='aio-red', title='Download Now')['href']
        fname = f'{path}{title.strip()}.cbz'
  
        outputformat.boxtitle('Loading comic...')

        r = SESSION.get(download_url, timeout=20)

        # Downloads the desired comic.
        with open(fname, 'wb') as file:
            # just works lmao
            total = int(r.headers['content-length'])
            progress = 0

            for chunk in r.iter_content(chunk_size=1024*512):
                progress += file.write(chunk)

                if not DEBUG:
                    # this might NOT be the best way to do this!
                    subprocess.run('clear', check=True)
                    outputformat.bar(progress, total, show_values=False, title=outputformat.b('Progress', return_str=True), title_pad=4, style='bar')
                
            outputformat.boxtitle('Download complete!')
            subprocess.run(f'open "{file.name}"', shell=True , check=True)

    except KeyError as e:
        print('something went wrong.')

        if DEBUG:
            print(e)



def find_comics(query: str, page):
    """Scrapes getcomics.info for comics that match @query"""
    response = SESSION.get(BASE_SEARCH_URL.replace('#', str(page)) + query, timeout=10)

    if response.status_code:
        doc = response.text
        parser = BeautifulSoup(doc, 'html.parser')

        comics = parser.find_all(attrs={'class' : 'post-header-image'})

        return comics

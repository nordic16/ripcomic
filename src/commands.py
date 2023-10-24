"""This module contains a few useful functions to handle all sorts of ripcomic's commands."""

import subprocess, tempfile, requests, outputformat
from bs4 import BeautifulSoup
from ripcomic import BASE_SEARCH_URL, HEADERS, SESSION


def comic_command(comic, page, path):
    """This function handles the comic command."""
    comics = find_comics(comic, page)

    # In order to pass arguments onto fzf, create a temporary file that fzf will be accessing.
    with tempfile.NamedTemporaryFile() as tf:
        for (index, c) in enumerate(comics):
            data = f'{index} - {c.a.img["alt"]}\n'
            tf.write(data.encode('utf-8'))

        try:
            tf.seek(0) # Seek pos needs to be set to the beginning before allowing fzf to read from the file.

            # Actually does the job lmao
            p = subprocess.check_output("fzf", stdin=tf)
            title = p.decode('utf-8')

            comic_url = comics[int(title[0])].a['href'] 
            title = title[title.find('-') + 1:].strip() # removes index to display to user later

            download_comic(comic_url, title, path)

        finally:
            tf.close() # This will also remove tf from the filesystem.



### HELPERS
def download_comic(comic_url: str, title: str, path: str):
    comic_page_parser = BeautifulSoup(SESSION.get(comic_url, timeout=15, headers=HEADERS).text, 'html.parser')

    try:
        download_url = comic_page_parser.find('a', class_="aio-red", title='Download Now')['href']
        fname = f'{path}{title.strip()}.cbz'
        
        r = SESSION.get(download_url, timeout=20, headers=HEADERS)

        # Downloads the desired comic.
        with open(fname, 'wb') as file:
            # just works lmao
            total = int(r.headers['content-length'])
            progress = 0

            for chunk in r.iter_content(chunk_size=1024*512):
                progress += file.write(chunk)

                # this might NOT be the best way to do this lmao.
                subprocess.run("clear", check=True)
                outputformat.bar(progress, total, show_values=False, title="Progress", title_pad=4)


            outputformat.boxtitle("Download complete!")

            subprocess.run(f'open "{file.name}"', shell=True , check=True)



    except KeyError:
        print("something went wrong.")


def find_comics(query: str, page):
    response = SESSION.get(BASE_SEARCH_URL.replace('#', str(page)) + query, timeout=10, headers=HEADERS)

    if response.status_code:
        doc = response.text
        parser = BeautifulSoup(doc, 'html.parser')

        comics = parser.find_all(attrs={'class' : 'post-header-image'})

        return comics

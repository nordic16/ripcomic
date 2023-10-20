from bs4 import BeautifulSoup
import requests, argparse, shutil, subprocess, os, tempfile

BASE_SEARCH_URL='https://getcomics.info/page/#/?s='


def download_comic(comic_url: str, title: str, comics):
    comic_page_parser = BeautifulSoup(requests.get(comic_url, timeout=10).text, 'html.parser')

    try:
        download_url = comic_page_parser.find('a', attrs={'class', 'aio-red'})['href']
        fname = f'{title}.cbz'
        r = requests.get(download_url, timeout=10)
        
        # Downloads the desired comic.
        with open(fname, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

    except KeyError:
        print("something went wrong.")


def find_comics(query: str, page=0):
    response = requests.get(BASE_SEARCH_URL.replace('#', str(page)) + query, timeout=10)
    
    if response.status_code:
        doc = response.text
        parser = BeautifulSoup(doc, 'html.parser')
        
        comics = parser.find_all(attrs={'class' : 'post-header-image'})

        return comics


def main():
    if not shutil.which("fzf"): # if fzf is not installed.
        print("fzf is not installed on $PATH")
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("--comic")
    args = parser.parse_args()

    if args.comic:
        comics = find_comics(args.comic)
        
        # In order to pass arguments onto fzf, create a temporary file that fzf will be accessing.
        with tempfile.NamedTemporaryFile() as tf:
            for (index, comic) in enumerate(comics):
                data = f'{index} - {comic.a.img["alt"]}\n'
                tf.write(data.encode('utf-8'))

            try:
                tf.seek(0)
                # Actually does the job lmao
                p = subprocess.check_output("fzf", stdin=tf)
                title = p.decode('utf-8')

                comic_url = comics[int(title[0])].a['href']

                download_comic(comic_url, title, comics)

            finally:
                tf.close()


            

if __name__ == '__main__':
    main()


BASE_SEARCH_URL=f'https://getcomics.info/page/#/?s='
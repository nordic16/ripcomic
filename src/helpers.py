"""This module contains a few useful functions to handle all sorts of ripcomic's commands."""
import outputformat, subprocess, configparser, os, tempfile
from bs4 import BeautifulSoup
from settings import BASE_SEARCH_URL, SESSION, DEBUG, DEFAULT_CONFIG_PATH

### HELPERS
def initialize_config():
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read(os.path.expanduser('~/.config/ripcomic.ini'))
    return parser


def download_comic(comic_url: str, title: str, path: str):
    """Downloads the comic onto the file system. Returns file path."""
    comic_page_parser = BeautifulSoup(SESSION.get(comic_url, timeout=15).text, 'html.parser')

    try:
        download_url = comic_page_parser.find('a', class_='aio-red', title='Download Now')['href']
        fname = f'{path}{title.strip()}.cbz'
        r = SESSION.get(download_url, timeout=20)

        outputformat.boxtitle('Loading comic...')


        # Downloads the desired comic.
        with open(os.path.expanduser(fname), 'wb') as file:
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


def find_comics(query: str, page: int):
    """Scrapes getcomics.info for comics that match @query"""
    url = BASE_SEARCH_URL.replace('#', str(page)) + query
    response = SESSION.get(url, timeout=15)

    if response.status_code:
        doc = response.text
        parser = BeautifulSoup(doc, 'html.parser')

        return parser.find_all(attrs={'class' : 'post-header-image'})

    return None


def write_to_conf(section: str, option: str, value: str):
    """Quick and convenient way to write something to config."""
    config = initialize_config()

    with open(DEFAULT_CONFIG_PATH, 'wt') as cfg:
        config.set(section, option, value)
        config.write(cfg)


def list_files_fzf(data):
    """Convenient way to list files on fzf and return the output."""
    with tempfile.NamedTemporaryFile() as tf:
        tf.writelines(data)
        tf.seek(0)

        output = subprocess.check_output('fzf', stdin=tf).decode('utf-8').strip()
        return output


def list_files(path: str, show_full_path: bool, values_to_return=[]):
    """returns all files within a directory."""
    full_path = os.path.expanduser(path)

    # There's probably no need to include hidden files.
    files = [x for x in os.listdir(full_path) if not x.startswith('.')]

    for f in files:
        abs_path = f'{full_path}/{f}'
        if os.path.isdir(abs_path):
            list_files(abs_path, show_full_path, values_to_return)

        else:
            val = abs_path if show_full_path else os.path.basename(abs_path)
            values_to_return.append(val)

    return values_to_return

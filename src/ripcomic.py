import argparse, shutil, requests, outputformat, subprocess, tempfile
import helpers

BASE_SEARCH_URL='https://getcomics.org/page/#?s='
SESSION = requests.session()
DEBUG = False

def main():
    SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding': 'gzip'})

    if not shutil.which('fzf'): # if fzf is not installed.
        print('fzf is not installed on $PATH')
        exit()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Command to scrape comics 
    comicparser = subparsers.add_parser('comic')
    comicparser.add_argument('comic', action='store')
    comicparser.add_argument('--page', action='store', type=int, default=1)
    comicparser.add_argument('--path', action='store', type=str, default='')
    comicparser.set_defaults(func=comic_command)

    libraryparser = subparsers.add_parser('set-library')
    libraryparser.add_argument('library')
    
    args = parser.parse_args()
    args.func(args)


def comic_command(args):
    """This function handles the comic command."""
    comic = args.comic
    page = args.page
    path = args.path

    comics = helpers.find_comics(comic, page)

    # In order to pass arguments onto fzf, create a temporary file that fzf will be accessing.
    with tempfile.NamedTemporaryFile() as tf:
        for (index, c) in enumerate(comics):
            data = f'{index} - {c.a.img["alt"]}\n'
            tf.write(data.encode('utf-8'))

        try:
            tf.seek(0) # Seek pos needs to be set to the beginning before allowing fzf to read from the file.

            # Actually does the job lmao
            p = subprocess.check_output('fzf', stdin=tf)
            title = p.decode('utf-8')

            comic_url = comics[int(title[0])].a['href']
            title = title[title.find('-') + 1:].strip() # removes index to display to user later

            helpers.download_comic(comic_url, title, path)

        except subprocess.CalledProcessError as e:
            print(f'Something went wrong! Make sure {page} isn\'t a huge number or try again later.')

            if DEBUG:
                print(e)

        finally:
            tf.close() # This will also remove tf from the filesystem.



if __name__ == '__main__':
    main()

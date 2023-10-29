import argparse, shutil, subprocess, tempfile, os
import helpers
from settings import DEBUG, SESSION, DEFAULT_CONFIG_PATH

def main():
    SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding': 'gzip'})

    if not shutil.which('fzf'): # if fzf is not installed.
        print('fzf is not installed on $PATH')
        exit()

    config = helpers.initialize_config()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Command to scrape comics
    comicparser = subparsers.add_parser('comic')
    comicparser.add_argument('comic', action='store')
    comicparser.add_argument('--page', action='store', type=int, default=1)
    comicparser.add_argument('--path', action='store', default=config.get('Settings', 'library-path'))
    comicparser.set_defaults(func=comic_command)

    setlibraryparser = subparsers.add_parser('set-library')
    setlibraryparser.add_argument('library')
    setlibraryparser.set_defaults(func=set_library_command)

    libraryparser = subparsers.add_parser('library')
    libraryparser.add_argument('--list', action='store_true')
    libraryparser.set_defaults(func=library_command)

    args = parser.parse_args()
    args.func(args)


### COMMANDS
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
            # Seek pos needs to be set to the beginning before allowing fzf to read from the file.
            tf.seek(0)

            # Actually does the job lmao
            p = subprocess.check_output('fzf', stdin=tf)

            title = p.decode('utf-8')
            comic_url = comics[int(title[0])].a['href']
            # removes index to display to user later
            title = title[title.find('-') + 1:].strip()

            helpers.download_comic(comic_url, title, path)

        except subprocess.CalledProcessError as e:
            print('Something went wrong!')

            if DEBUG:
                print(e)

        finally:
            # This will also remove tf from the filesystem.
            tf.close()


def set_library_command(args):
    """Handles the set-library command"""
    config = helpers.initialize_config()
    path = os.path.expanduser(args.library)

    if os.path.isdir(path):
        with open(DEFAULT_CONFIG_PATH, 'wt') as cfg:
            config.set(section="Settings", option="library-path", value=path)
            config.write(cfg)

    else:
        print("Invalid path.")


def library_command(args):
    """Handles the library command"""
    config = helpers.initialize_config()
    library_path = os.path.expanduser(config.get("Settings", "library-path"))

    # removes trailing / if needed:
    library_path = library_path[:-1] if library_path[-1] == '/' else library_path

    if args.list:
        data = helpers.list_files(os.path.expanduser(library_path), show_full_path=True)
        # Filters out non-comic files

        data = list(filter(lambda x: os.path.splitext(x)[1] == '.cbz' or os.path.splitext(x)[1] == '.cbr', data))
        data.sort()

        with tempfile.NamedTemporaryFile() as tf:
            tf.writelines([f'{os.path.basename(x)}\n'.encode('utf-8') for x in data])
            tf.seek(0)

            comicname = subprocess.check_output('fzf', stdin=tf).decode('utf-8').strip()
            # there are probably better ways to do this.
            comic = [x for x in data if comicname in x][0]
            subprocess.run(f'open "{comic}"', shell=True, check=True)

            tf.close()


if __name__ == '__main__':
    main()

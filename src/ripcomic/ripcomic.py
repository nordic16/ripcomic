import argparse, shutil, subprocess, os, outputformat
import helpers
from settings import DEBUG, SESSION, MAX_HISTORY_SIZE
def main():
    SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding': 'gzip'})

    if not shutil.which('fzf'):
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
    libraryparser.add_argument('action', action='store', choices=['list', 'remove', 'last-read'])
    libraryparser.set_defaults(func=library_command)

    historyparser = subparsers.add_parser('history')
    historyparser.add_argument('--last', action='store', type=int)
    historyparser.set_defaults(func=history_command)

    sethistory_parser = subparsers.add_parser('set-history')
    sethistory_parser.add_argument('size', action='store', type=int)
    sethistory_parser.set_defaults(func=set_history_size)

    try:
        args = parser.parse_args()
        args.func(args)

    except subprocess.CalledProcessError as e:
        print('Something went wrong. Did you select any comics?')

        if DEBUG:
            print(e)


#### COMMANDS
def comic_command(args):
    """This function handles the comic command."""
    comic = args.comic
    page = args.page
    path = args.path

    comics = helpers.find_comics(comic, page)
    data = [f'{index} - {c.a.img["alt"]}\n'.encode('utf-8') for (index, c) in enumerate(comics)]
    comic = helpers.list_files_fzf(data)
    comic_url = comics[int(comic[0])].a['href']

    # removes index to display to user later
    comic = comic[comic.find('-') + 1:].strip()

    path = helpers.download_comic(comic_url, comic, path)
    helpers.open_comic(path)


def set_library_command(args):
    """Handles the set-library command"""
    path = os.path.expanduser(args.library)

    if os.path.isdir(path):
        helpers.write_to_conf('Settings', 'library-path', path)

    else:
        print("Invalid path.")


def library_command(args):
    """Handles the library command"""
    config = helpers.initialize_config()
    library_path = os.path.expanduser(config.get("Settings", "library-path"))

    data = helpers.list_files(os.path.expanduser(library_path), show_full_path=True)

    # Filters out non-comic files
    data = list(filter(lambda x: os.path.splitext(x)[1] in ('.cbr', '.cbz'), data))
    data.sort()

    if args.action == 'list':
        comicname = helpers.list_files_fzf([f'{os.path.basename(x)}\n'.encode('utf-8') for x in data])
        comic = [x for x in data if comicname in x][0]
        helpers.open_comic(comic)

    elif args.action == 'remove':
        comic = helpers.list_files_fzf([f'{os.path.basename(x)}\n'.encode('utf-8') for x in data])
        comic = [x for x in data if comicname in x][0]

        ans = input(f'Are you sure you want to delete "{comicname}"? (y/n): ').lower()
        outputformat.br()

        if ans in ('y', 'yes'):
            os.remove(comic)
            outputformat.boxtitle(f'{comicname} deleted successfully.', style='#', bold=True)

        else:
            outputformat.boxtitle('Huh?', style='#', bold=True)

    elif args.action == 'last-read':
        last_read = config.get('General', 'last-read')
        print(f'Last read: {last_read if last_read else "Read some comics."}')

        outputformat.br()


def history_command(args):
    """Handles the history command"""
    config = helpers.initialize_config()
    history = config.get('General', 'history').strip().splitlines()
    history_size = config.getint('Settings', 'history-size') 

    # Makes sure the code below will never go out of bounds.
    i = history_size if args.last > history_size or args.last < 1 else args.last

    for j in range(i):
        print(f'({j + 1}) {history[j]}')


def set_history_size(args):
    """handles the set-history command."""
    if args.size > MAX_HISTORY_SIZE: # 70 seems a reasonable max size
        print(f'{args.size} > {MAX_HISTORY_SIZE}! Choose a smaller number.')

    elif args.size < 1:
        print(f'{args.size} < 1... Why.')

    else:
        helpers.write_to_conf('Settings', 'history-size', str(args.size))

if __name__ == '__main__':
    main()

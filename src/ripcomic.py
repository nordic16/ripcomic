import argparse, shutil, subprocess, tempfile, os, outputformat
import helpers
from settings import DEBUG, SESSION, DEFAULT_CONFIG_PATH

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
        tf.writelines([f'{index} - {c.a.img["alt"]}\n'.encode('utf-8') for (index, c) in enumerate(comics)])

        try:
            # Seek pos needs to be set to the beginning before allowing fzf to read from the file.
            tf.seek(0)

            # Actually does the job lmao
            p = subprocess.check_output('fzf', stdin=tf)
            config = helpers.initialize_config()

            title = p.decode('utf-8')
            comic_url = comics[int(title[0])].a['href']
            
            # removes index to display to user later
            title = title[title.find('-') + 1:].strip()

            helpers.download_comic(comic_url, title, path)
            helpers.write_to_conf('General', 'last-read', title)

        except subprocess.CalledProcessError as e:
            print('Something went wrong!')

            if DEBUG:
                print(e)

        finally:
            # This will also remove tf from the filesystem.
            tf.close()


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

    # removes trailing / if needed
    library_path = library_path[:-1] if library_path[-1] == '/' else library_path
    data = helpers.list_files(os.path.expanduser(library_path), show_full_path=True)

    # Filters out non-comic files
    data = list(filter(lambda x: os.path.splitext(x)[1] in ('.cbr', '.cbz'), data))
    data.sort()

    # This code is outside the 1st and 2nd if statement in order to reduce repetition, despite not being used in the 'last-read' command.
    with tempfile.NamedTemporaryFile() as tf:
        tf.writelines([f'{os.path.basename(x)}\n'.encode('utf-8') for x in data])
        tf.seek(0)

        # TODO: lines common to 'list' and 'remove' should be their own separate function.
        if args.action == 'list':
            comicname = subprocess.check_output('fzf', stdin=tf).decode('utf-8').strip()
            # there are probably better ways to do this.
            comic = [x for x in data if comicname in x][0]
            subprocess.run(f'open "{comic}"', shell=True, check=True)
            helpers.write_to_conf('General', 'last-read', comicname)

        elif args.action == 'remove':
            comicname = subprocess.check_output('fzf', stdin=tf).decode('utf-8').strip()
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
        tf.close()



if __name__ == '__main__':
    main()

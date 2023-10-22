import argparse, shutil
import commands

BASE_SEARCH_URL='https://getcomics.info/page/#/?s='


def main():
    if not shutil.which("fzf"): # if fzf is not installed.
        print("fzf is not installed on $PATH")
        exit()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Parser for comics section
    comicparser = subparsers.add_parser("comic")
    comicparser.add_argument("comic", action='store')
    comicparser.add_argument("--page", action='store', type=int, default=1)
    comicparser.add_argument("--path", action='store', type=str, default='.')
    args = parser.parse_args()
    

    if args.comic:
        commands.comic_command(args.comic, args.page, args.path)


if __name__ == '__main__':
    main()

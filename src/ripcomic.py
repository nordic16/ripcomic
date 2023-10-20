from bs4 import BeautifulSoup
import requests


BASE_SEARCH_URL=f'https://getcomics.info/page/#/?s='

# TODO: TURN THIS APP INTO CLI. USE THIS CODE AS INSPIRATION.

def main():
    print('\x1b[1;33m• Welcome to xcsr, the comic scraper.\n')
    
    query = input('\x1b[1;33m· Query: ').replace(' ', '+')
    page = int(input('\x1b[1;33m· Page: '))
    
    response = requests.get(BASE_SEARCH_URL.replace('#', str(page)) + query)
    
    if response.status_code == requests.codes.ok:
        doc = response.text
        parser = BeautifulSoup(doc, 'html.parser')
        
        comics = parser.find_all(attrs={'class' : 'post-header-image'})       
        
        for (index, comic) in enumerate(comics, start=1):
            print(f'\x1b[1;33m· ({index}) - {comic.a.img["alt"]}')
        
        val = int(input("\n\x1b[1;33m· Type in the index of the comic you'd like to download: ")) - 1
        
        comic_url = comics[val].a['href']
        
        comic_page_parser = BeautifulSoup(requests.get(
            comic_url).text, 'html.parser')

        try:
            download_url = comic_page_parser.find('a', attrs={'class', 'aio-red'})['href']
            fname = f'{comics[val].img["alt"]}.cbz'
            r = requests.get(download_url)
            
            # Downloads the desired comic.
            with open(fname, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
            
            print(f'\n\x1b[1;33m· Finished downloading "{fname}"!')
                
        except KeyError:
            print("\x1b[1;31m· Couldn't retrieve download url.")    
            print(f"\x1b[1;31m· Here's the page url: {comic_url}")    
        
            

if __name__ == '__main__':
    main()
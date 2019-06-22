from PttWebCrawler.crawler import *

def crawl():
    crawler = PttWebCrawler(as_lib=True)
    crawler.parse_articles(500, crawler.getLastPage('Gossiping'), 'Gossiping')

if __name__ == "__main__":
    crawl()
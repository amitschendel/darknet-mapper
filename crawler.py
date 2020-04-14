import core


def main():
    crawler = core.tor()
    headers = {

        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'referer': 'https://www.google.com'
    }
    links = list(set(crawler.get_unchecked_links()))

    for count, link in enumerate(links):
        link = link.strip()
        print("current link: {}".format(link))
        print("links count: {}".format(len(links)))
        print("links left: {}".format(len(links)-count))
        if not crawler.is_link_exist(link):
            page = crawler.request_page(link, headers)
            if page:
                try:
                    crawler.parse_page(page, link)
                except:
                    pass
        else:
            print("link already exist, moving on")


if __name__ == "__main__":
    main()

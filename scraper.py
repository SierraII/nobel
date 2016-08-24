import os, sys
import formatter
import htmllib
import urllib

class LinksExtractor(htmllib.HTMLParser):

    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)
        self.links = []

    def start_a(self, attrs):

        # process the attributes
        if len(attrs) > 0:
            for attr in attrs:
                if attr[0] == "href":
                    self.links.append(attr[1])

    def get_links(self):
        return self.links

class Scraper:

    unparsed_links = []
    current_links = []
    parsed_links = []

    def __init__(self, url):
        if not url.startswith("http://"):
            url = "http://" + url
        if url.endswith("/"):
            url = url[0:len(url) - 1]

        self.base_url = url
        self.unparsed_links.append(url)
        self.get_links()

    def get_links(self):

        format = formatter.NullFormatter()
        htmlparser = LinksExtractor(format)
        if not len(self.unparsed_links) == 0:

            self.current_links = []

            for link in self.unparsed_links:

                print "Parsing: " + link
                data = urllib.urlopen(link)

                htmlparser.feed(data.read())
                htmlparser.close()

                self.current_links = htmlparser.get_links()
                self.parsed_links.append(link)
                self.unparsed_links.remove(link)
                self.sort_links()

            self.get_links()

    def sort_links(self):

        for link in self.current_links:
            link = self.format_link(link)

            if link not in self.parsed_links:

                if link not in self.unparsed_links:

                    if link is not None:
                        self.unparsed_links.append(link)

    def format_link(self, link):

        htm_formats = [".htm", ".php", ".txt", ".asp", ".cgi", ".pl"]
        image_types = [".gif", ".jpg", ".png"]
        is_hf = False

        for image_type in image_types:
            if image_type in link:
                return None

        if "." in link:
            for hf in htm_formats:
                if hf in link:
                    is_hf = True
            if not hf:
                return None

        if link.endswith('/'):
            link = link[0: len(link) - 1]
        if link.startswith('#'):
            return None
        if link.startswith('/'):
            return self.base_url + link
        if self.base_url in link:
            return link
        if link.startswith("http://") and link not in self.base_url in link:
            return None

    def generate_map(self, output):

        xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        xml += "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.sitemaps.org/schemas/sitemap/0.9\thttp://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd\">"

        utils = Utils()

        for link in self.parsed_links:

            priority = 0.5
            split = link.split("/")

            if utils.has_numbers(split[-1]) is True:
                priority = 0.8

            xml += "<url><loc>" + link + "</loc><changefreq>weekly</changefreq><priority>" + str(priority) + "</priority></url>"

        xml += "</urlset>"

        return xml


    def get_list(self):

        return self.parsed_links

class Utils:

    def has_numbers(self, string):
        return any(char.isdigit() for char in string)


scraper = Scraper("http://www.wantedonline.co.za")
xml = scraper.generate_map("out.xml")

print xml

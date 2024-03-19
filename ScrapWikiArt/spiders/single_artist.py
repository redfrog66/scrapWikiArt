# scrapy runspider -o data/data.csv -t csv ScrapWikiArt/spiders/single_artist.py

import scrapy
from bs4 import BeautifulSoup
from ScrapWikiArt.items import CustomImageItem

class SingleArtistSpider(scrapy.Spider):
    name = "single_artist"
    allowed_domains = ["wikiart.org"]
    domain = "wikiart.org"
    artist = "gustav-klimt" # giovanni-battista-piranesi / gustav-klimt
    start_urls = ["https://www.wikiart.org/en/${artist}/all-works/text-list"]
    id = 0
    custom_settings = {
        "ITEM_PIPELINES": {
            'ScrapWikiArt.pipelines.CustomImagesPipeline': 1,
        },
        "IMAGES_STORE": "data/img/${artist}",
    }

    def parse(self, response):
        for item in response.xpath('//main/div/ul/li/a/@href').getall():
            yield response.follow(item, callback=self.parse_item)

    def parse_item(self, response):
        url = response.url
        title = response.xpath("//article/h3/text()").get()
        original_title_raw = response.xpath("//li[.//s[text()[contains(.,'Original Title:')]]]").get()
        original_title = original_title_raw.replace("<li>\n            <s>Original Title:</s>\n            ", '')\
            .replace("\n        </li>", '') if original_title_raw else original_title_raw
 
        styles = response.xpath("//li[.//s[text()[contains(.,'Style:')]]]/span/a/text()").getall()

        genre = response.xpath("//li[.//s[text()[contains(.,'Genre:')]]]/span/a/span[@itemprop='genre']/text()").get()

        media = response.xpath("//li[.//s[text()[contains(.,'Media:')]]]/span/a/text()").getall()

        description_raw = response.xpath('//div[@id="info-tab-description"]/p').get()
        description = BeautifulSoup(description_raw, features="lxml").get_text() if description_raw else description_raw

        wiki_description_raw = response.xpath('//div[@id="info-tab-wikipediadescription"]/p').get()
        wiki_description = BeautifulSoup(wiki_description_raw, features="lxml").get_text() if wiki_description_raw else wiki_description_raw

        tags = response.xpath("//div[@class='tags-cheaps']/div/a/text()").getall()
        tags = [tag.replace('\n', '').replace('\t', '').replace(' ', '') for tag in tags]

        img_urls = response.xpath('//ul[@class="image-variants-container"]//a/@data-image-url').getall()

        if not img_urls:
            img_urls = [response.xpath('//img[@itemprop="image"]/@src').get()]
        # img = f"img/full/{hashlib.sha1(img_url.encode()).hexdigest()}.{img_url.split('.')[-1]}"

        item = CustomImageItem({
            "Id": self.id,
            "URL": url,
            "Title": title,
            "OriginalTitle": original_title,
            "Styles": styles,
            "Genre": genre,
            "Media": media,
            "Description": description,
            "WikiDescription": wiki_description,
            "Tags": tags,
            "image_urls": img_urls,
        })
        self.id += 1
        yield item

        

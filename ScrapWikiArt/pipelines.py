# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapwikiartPipeline:
    def process_item(self, item, spider):
        return item

import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem

class CustomImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = request.url.split('/')[-1].split('.')[0]  # extract the image number from the URL
        artist_name = "piranesi"  # piranesi / klimt
        return f'{artist_name}_image{image_guid}.jpg'

    def get_media_requests(self, item, info):
        for img_url in item['image_urls']:
            yield Request(img_url, meta={'item': item})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        
        # Rename the image file
        old_path = os.path.join(self.store.basedir, image_paths[0])
        new_filename = self.file_path(Request(item['image_urls'][0]), item=item)
        new_path = os.path.join(self.store.basedir, new_filename)
        os.rename(old_path, new_path)

        # Update the images field in the item
        item['images'] = [{'path': new_filename}]
        return item
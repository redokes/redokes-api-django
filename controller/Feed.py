from redokes.controller.Crud import Crud
from django.utils import feedgenerator
from django.http import HttpResponse

""" 
Abstract the field names in rss_action to reference the parent class definitions
"""

class Feed(Crud):

    def __init__(self, *args, **kwargs):
        #Add additional variables
        self.rss_feed = False
        self.title = ''
        self.link = ''
        self.description = ''
        self.item_title = ''
        self.item_link = '' 
        self.item_description = ''
        self.item_pubdate = ''
        self.item_author_name = ''
        self.item_category_name = ''
        self.item_slug = ''
        
        #Call parent
        Crud.__init__(self, *args, **self.util.config(
            kwargs,
            output_type = 'rss'
        ))
    
    def rss_action(self):
        self.lookup_instance.add_sorter('published_at', 'desc')
        self.lookup_instance.add_filter('published', 1)
        self.read_action()
        self.rss_feed = feedgenerator.Rss201rev2Feed(
            title = self.title,
            link = self.link,
            description = self.description
        )
        
        for item in self.lookup_instance.get_models():
            self.rss_feed.add_item(
                title = getattr(item, self.item_title),
                link = self.get_item_link(item),
                description = self.get_item_description(item),
                pubdate = getattr(item, self.item_pubdate),
                author_name = self.get_author_name(item)
            )
            
    def get_item_description(self, item):
        return getattr(item, self.item_description)
    
    def get_author_name(self, item):
        return getattr(item, self.item_author_name)
            
    def get_item_link(self, item):
        return ''
    
    def get_rss_string(self):
        if self.rss_feed:
            return 
            
    def get_output_rss(self):
        return HttpResponse(self.rss_feed.writeString('UTF-8'), mimetype="application/rss+xml")
    
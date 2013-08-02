from urlparse import urlparse
from os import path
import re


class URLClassifier(object):
    """
    Classify all the tweets
 
    """
    output_format = 'json'
 
    def __init__(self):
        self.videos = ['youtube', 'vimeo']
        self.imgs = ['.jpg', '.png', '.gif']
        self.ignoreDomain = ['facebook', 'foursquare', '4sq', 'instagram']
        self.ignoreExt = ['.pdf']
 
    def classify_url(self, url):
        _, root, url_path, params, query, fragment = urlparse(url)

        for domain in self.videos:
            if domain in root:
                return 'video'

        for domain in self.ignoreDomain:
            if domain in root:
                return None

        if len(url_path) <= 1:
            return 'front_page'

                
        ext = path.splitext(url_path)

        if ext in self.ignoreExt:
            return None
        
        if ext in self.imgs:
            return 'img'

        return 'article'
 
    
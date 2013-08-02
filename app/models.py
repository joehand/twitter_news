from app import app, db
from app.diffbot import Diffbot
from datetime import datetime
from mongoengine import signals

diffbot = Diffbot(app.config['DIFFBOT_TOKEN'])

def update_multiple(document, update_dict):
    for key, val in update_dict.iteritems():
        if key not in ['id', 'status']:
            setattr(document, key, val)

class User(db.DynamicDocument):
    user_id = db.StringField(primary_key=True, required=True)
    screen_name = db.StringField(required=True)
    oauth_token = db.StringField(required=True)
    oauth_token_secret = db.StringField(required=True)
    full_profile = db.BooleanField(default=False, required=True)
    max_id = db.IntField(default=0, required=True)
    tweets = db.ListField(db.ReferenceField('Tweet'))

    def get_full_profile(self, twitterAPI):
        update_multiple(self, twitterAPI.show_user(screen_name=self.screen_name))
        self.full_profile = True
        self.save()

    def get_tweets(self):
        return [tweet for tweet in self.tweets]

class Tweet(db.DynamicDocument):
    tweet_id = db.StringField(primary_key=True, required=True)
    article = db.ReferenceField('Article')

    def flatten(self):
        return dict(self.to_mongo().to_dict()).update(self.article.to_mongo().to_dict())

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        url = document.entities['urls'][0]['expanded_url']
        article = Article.objects.get_or_create(url = url)
        document.article = article[0].to_dbref()

    meta = {
        'indexes': ['-tweet_id'],
        'ordering': ['-tweet_id']
    }

signals.pre_save.connect(Tweet.pre_save, sender=Tweet)

class Article(db.DynamicDocument):
    """
        Store each article in commonly accesible DB. 
        
        Information from twitter for a url:
            - Tweet text
            - Tweet time
            - Tweet user
            - URLS (short, expanded, display)
            - Indicies (where in tweet url is)
            - Retweet Count
            - Favorite Count
            - ... More

        DiffBot Returns (from Article API):
            - Text/html
            - Title
            - Date
            - Author
            - Media
            - Meta Information
            - Tags
    """

    url = db.URLField(required=True)
    displayUrl = db.StringField()
    title = db.StringField()
    html = db.StringField()
    date = db.StringField()
    article_fetched = db.BooleanField(default=False, required=True)


    def __unicode__(self):
        return unicode(self.url)

    def get_id(self):
        return unicode(self.id)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        if not document.article_fetched:
            print 'fetcthing bot contents'
            print document.url
            bot_contents = diffbot.get_article({
                                    'url': document.url,
                                    'html':True,
                                    'meta':True,
                                    'tags':True,
                                    'summary':True
                                })

            if 'errorCode' not in bot_contents:
                document.title = bot_contents['title']
                document.html = bot_contents['html']
                document.tags = bot_contents['tags']
                document.meta = bot_contents['meta']

                if 'resolved_url' in bot_contents:
                    document.url = bot_contents['resolved_url']

                if 'date' in bot_contents:
                    document.date = bot_contents['date']

                document.article_fetched = True
        print 'done fetching bot contents'

    meta = {
        'indexes': ['-date'],
        'ordering': ['-date']
    }

signals.pre_save.connect(Article.pre_save, sender=Article)


class FrontPage(db.Document):
    url = db.URLField(required=True)
    """
    Deal with front pages or ignore them?
    tweet['bot_contents'] = diffbot.get_frontpage({
                                'url': url,
                            })

    #finalTweets.append(tweet)
    """
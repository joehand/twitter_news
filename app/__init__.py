import os
from flask import Flask

from flask_debugtoolbar import DebugToolbarExtension

from mongoengine import connect
from flask.ext.mongoengine import MongoEngine

from flask.ext.bootstrap import Bootstrap


app = Flask(__name__)
app.debug = True

# set the secret key for sessions.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Twitter/Requests is not happy if I load config from object. WHY?!?!
app.config.update(
    # Bootstrap Config (https://github.com/mbr/flask-bootstrap#configuration-options)
    BOOTSTRAP_USE_CDN = True,

    # Twitter API Information (https://dev.twitter.com/apps/
    TWITTER_KEY = 'tONPCz21dNB4qQoC4Kh8vA',
    TWITTER_SECRET = 'tuzy6saYVlQEaUDqRhefwQ7YsQU0CBOEu5tHYtYnYDQ',
    CALLBACK_URL = 'http://127.0.0.1:8000/callback',

    #MongoDB Info
    DB_NAME = 'app17259527',
    DB_USERNAME = 'heroku',
    DB_PASSWORD = 'app17259527MONGOHQ',
    DB_HOST_ADDRESS = 'dharma.mongohq.com:10015/app17259527',

    # Diffbot! (http://diffbot.com/products/automatic/article/)
    DIFFBOT_TOKEN = '08ebd2316a465a97fc4d98feb8fed326',
)

#DATABASE Connection
app.config['MONGODB_DB'] = os.environ.get('DB_NAME') or app.config['DB_NAME']

#For Heroku MongoHQ Add-On
if os.environ.get('MONGOHQ_URL'):
    connect(app.config['DB_NAME'], host=os.environ.get('MONGOHQ_URL'))
else:
    connect(app.config['DB_NAME'], host=('mongodb://' + app.config['DB_USERNAME'] + 
                                         ':' + app.config['DB_PASSWORD'] + '@' + 
                                         app.config['DB_HOST_ADDRESS']))

app.config['DEBUG_TB_PANELS'] = (
    'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
    'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
    'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
    'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
    'flask.ext.mongoengine.panels.MongoDebugPanel'
)

#Add various extensions
toolbar = DebugToolbarExtension(app)
db = MongoEngine(app)
Bootstrap(app)


# Import the rest
from app import views, models
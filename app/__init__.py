from flask import Flask
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

# App config
app.debug = True

# Bootstrap Config (https://github.com/mbr/flask-bootstrap#configuration-options)
app.config.update(
    BOOTSTRAP_USE_CDN = True
    )

# Twitter API Information (https://dev.twitter.com/apps/)
app.config.update(
    TWITTER_KEY = 'tONPCz21dNB4qQoC4Kh8vA',
    TWITTER_SECRET = 'tuzy6saYVlQEaUDqRhefwQ7YsQU0CBOEu5tHYtYnYDQ',
    CALLBACK_URL = 'http://127.0.0.1:8000/callback'
    )

# Diffbot! (http://diffbot.com/products/automatic/article/)
app.config['DIFFBOT_TOKEN'] = '08ebd2316a465a97fc4d98feb8fed326'


# set the secret key for sessions.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


from app import views

from app import app
from models import Article, User, Tweet

from flask import session, redirect, url_for, request, render_template, g, flash
from twython import Twython

from app.url_classier import URLClassifier

# this code is really helpful: https://code.google.com/p/gabr/
urlClass = URLClassifier()

@app.before_request
def before_request():
    if not getattr(g, 'user', None):
        if not getattr(g, 'twitter', None):
            g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'])

        oauth_token = None
        oauth_token_secret = None

        g.user_id = session.get('user_id')
        if g.user_id:
            oauth_token = session['oauth_token']
            oauth_token_secret = session['oauth_token_secret']
        if oauth_token and oauth_token_secret:
            g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'],
                oauth_token, oauth_token_secret)
            g.user = User.objects(user_id = g.user_id).first()


@app.route('/')
def index():
    if getattr(g, 'user', None):
        user = g.user

        if not user.full_profile:
            user.get_full_profile(g.twitter)

        if len(user.tweets) > 0:
            timeline = g.twitter.get_home_timeline(
                        since_id=user.tweets[0].id, 
                        max_id=user.max_id
                    )
        else:
            timeline = g.twitter.get_home_timeline()

        print 'got ' + str(len(timeline)) + ' new tweets'

        for tweet in timeline:
            if tweet['id'] > user.max_id:
                user.max_id = tweet['id']

            if len(tweet['entities']['urls'])>0:
                url = tweet['entities']['urls'][0]['expanded_url']

                urlType = urlClass.classify_url(url)

                if urlType  == 'front_page':
                    pass
                elif urlType == 'article':
                    tweet_id = str(tweet['id'])
                    tweet.pop('id') #complains if you pass this into defaults
                    tweet = Tweet.objects.get_or_create(tweet_id = tweet_id, defaults=tweet)
                    user.update(add_to_set__tweets=tweet[0].to_dbref())

        return render_template('hello.html', user=user, tweets=user.get_tweets())
    return render_template('hello.html')

@app.route('/login')
def login():
    if not 'user_id' in session:
        session.update(
                g.twitter.get_authentication_tokens(callback_url=app.config['CALLBACK_URL'])
        )

        return redirect(session['auth_url'])
    return redirect(url_for('index'))

@app.route('/callback')
def callback():
    g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'],
                    session['oauth_token'], session['oauth_token_secret'])

    session.update(g.twitter.get_authorized_tokens(request.args.get('oauth_verifier')))

    if 'user_id' in session:
        defaults = {
                        'screen_name' : session['screen_name'],
                        'oauth_token' : session['oauth_token'],
                        'oauth_token_secret' : session['oauth_token_secret']
                    }

        g.user = User.objects.get_or_create(user_id = session['user_id'], defaults=defaults)
        flash("Welcome. Here is some new news.", 'info')

    else:
        flash("Something went wrong! We weren't able to log you in", 'danger')

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('screen_name', None)
    session.pop('user_id', None)
    session.pop('oauth_token', None)
    session.pop('oauth_token_secret', None)
    g.user = None
    g.user_id = None
    g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'])

    return redirect(url_for('index'))

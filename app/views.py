from app import app

from flask import session, redirect, url_for, request, render_template, g
from twython import Twython

from app.diffbot import Diffbot
from app.url_classier import URLClassifier

# this code is really helpful: https://code.google.com/p/gabr/
diffbot = Diffbot(app.config['DIFFBOT_TOKEN'])
urlClass = URLClassifier()

@app.before_request
def before_request(): 
    g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'])

    oauth_token = None
    oauth_token_secret = None

    g.screen_name = session.get('screen_name')
    if g.screen_name:
        oauth_token = session['oauth_token']
        oauth_token_secret = session['oauth_token_secret']
    if oauth_token and oauth_token_secret:
        g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'],
            oauth_token, oauth_token_secret)

@app.route('/')
def index():
    if 'oauth_token_secret' in session:
        timeline = g.twitter.get_home_timeline()

        finalTweets = []

        for tweet in timeline:
            if len(tweet['entities']['urls'])>0:
                url = tweet['entities']['urls'][0]['expanded_url']

                urlType = urlClass.classify_url(url)

                if urlType  == 'front_page':
                    pass
                    """
                    Deal with front pages or ignore them?
                    tweet['bot_contents'] = diffbot.get_frontpage({
                                                'url': url,
                                            })

                    #finalTweets.append(tweet)
                    """
                elif urlType == 'article':

                    tweet['bot_contents'] = diffbot.get_article({
                                                'url': url,
                                                'html':True,
                                                'meta':True,
                                                'tags':True,
                                                'summary':True
                                            })

                    print tweet['bot_contents']['text']

                    finalTweets.append(tweet)


        user = g.twitter.show_user(screen_name=g.screen_name)

        return render_template('hello.html', timeline=finalTweets, user=user)
    return render_template('hello.html')

@app.route('/login')
def login():
    if not 'oauth_token_secret' in session:
        auth = g.twitter.get_authentication_tokens(callback_url=app.config['CALLBACK_URL'])

        session['oauth_token'] = auth['oauth_token']
        session['oauth_token_secret'] = auth['oauth_token_secret']

        return redirect(auth['auth_url'])
    return redirect(url_for('index'))

@app.route('/callback')
def callback():
    oauth_verifier = request.args.get('oauth_verifier')

    g.twitter = Twython(app.config['TWITTER_KEY'], app.config['TWITTER_SECRET'],
                    session['oauth_token'], session['oauth_token_secret'])

    session.update(g.twitter.get_authorized_tokens(oauth_verifier))
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('screen_name', None)
    session.pop('user_id', None)
    session.pop('oauth_token', None)
    session.pop('oauth_token_secret', None)
    return redirect(url_for('index'))

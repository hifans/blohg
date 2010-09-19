from flask import Module, make_response, current_app, request
from werkzeug.contrib.atom import AtomFeed, FeedEntry

from blohg.decorators import validate_locale
from blohg.filters import rst2html

atom = Module(__name__)

@atom.route('/<locale>/atom/')
@atom.route('/<locale>/rss/') # dumb redirect to keep the compatibility
@validate_locale
def atom_feed(locale):
    posts = current_app.hg.get_all(locale, True)
    posts = posts[:current_app.config['POSTS_PER_PAGE']]
    feed = AtomFeed(
        title = current_app.localized_config('TITLE'),
        subtitle = current_app.localized_config('TAGLINE'),
        url = request.url_root,
        feed_url = request.url_root + locale + '/atom/',
        author = current_app.config['AUTHOR'],
        generator = ('blohg', None, None)
    )
    for post in posts:
        mdatetime = post['mdatetime']
        if mdatetime is None:
            mdatetime = post['datetime']
        feed.add(
            FeedEntry(
                title = post['title'],
                content = rst2html(post.full),
                summary = rst2html(post.abstract),
                url = request.url_root + locale + '/'+ post.name +'/',
                author = current_app.config['AUTHOR'],
                published = post['datetime'],
                updated = mdatetime,
            )
        )
    response = make_response(str(feed))
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response
from myMood import db, cache
from flask_login import current_user
from myMood.models import User, Post


# start caching current_user
@cache.memoize()
def query_user_profile(user):
    return User.query.filter_by(username=user).first_or_404()


@cache.memoize()
def query_search_user(q_user):
    return User.query.filter(
        User.username.ilike("%" + q_user + "%"), current_user.username != q
    ).all()


@cache.memoize()
def query_search_stories(q_story):
    s = current_user
    return s.search_posts(q).all()

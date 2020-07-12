from myMood import db, cache
from flask_login import current_user
from myMood.models import User, Post

# start caching stories
@cache.memoize(timeout=50)
def query_all_public_stories():
    return Post.query.filter_by(state="public").order_by(Post.date_posted.desc()).all()


@cache.memoize(timeout=50)
def query_public_stories():
    return (
        Post.query.filter_by(state="public")
        .order_by(Post.date_posted.desc())
        .limit(7)
        .all()
    )


@cache.memoize(timeout=50)
def query_def_stories():
    s = current_user
    return s.followed_posts().limit(10).all()


@cache.memoize(timeout=50)
def query_all_stories():
    s = current_user
    return s.followed_posts().all()


@cache.memoize(timeout=50)
def query_all_user_stories(user):
    return Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()


@cache.memoize(timeout=50)
def query_user_story(story_id):
    return Post.query.get_or_404(story_id)


# end caching stories

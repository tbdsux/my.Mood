from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from myMood import db, cache
from myMood.models import User, Post
from myMood.stories.forms import NewStoryForm
from myMood.stories.query import (
    query_all_public_stories,
    query_all_stories,
    query_def_stories,
    query_all_user_stories,
    query_user_story,
)

stories = Blueprint("stories", __name__)


def is_post():
    return request.method == "POST"


@stories.route("/u/<user>/stories/<int:story_id>", methods=["GET"])
@cache.memoize()
def user_post(user, story_id):
    form = NewStoryForm()
    story = query_user_story(story_id)
    if request.method == "GET":
        form.content.data = story.content
        form.emotion.data = story.emotion
        form.state.data = story.state
    return render_template(
        "dashboard/user_post.html", story=story, dashboard_title="My Story", form=form,
    )


# update post
@stories.route("/u/<user>/stories/<int:story_id>/update", methods=["GET", "POST"])
def update_post(user, story_id):
    story = query_user_story(story_id)
    if story.author != current_user:
        return redirect(url_for("users.dash_profile", user=story.author.username))
    form = NewStoryForm()
    if request.method == "POST":
        if form.validate_on_submit():
            story.content = form.content.data
            story.emotion = form.emotion.data
            story.state = form.state.data
            db.session.commit()
            cache.delete_memoized(query_user_story, story_id)
            cache.delete_memoized(user_post)
            return redirect(
                url_for(
                    "stories.user_post", user=current_user.username, story_id=story.id
                )
            )


# delete post
@stories.route("/u/<user>/stories/<int:story_id>/delete", methods=["GET", "POST"])
def delete_post(user, story_id):
    story = query_user_story(story_id)
    if story.author != current_user:
        return redirect(url_for("users.dash_profile", user=story.author.username))
    if request.method == "POST":
        db.session.delete(story)
        db.session.commit()
        cache.delete_memoized(query_user_story, story_id)
        cache.delete_memoized(user_post)
        return redirect(url_for("users.dash_profile", user=current_user.username))


# GET ALL STORIES

# all stories with followed ones
@stories.route("/stories/all")
def all_stories():
    stories = query_all_stories()

    return render_template(
        "dashboard/all_stories.html", dashboard_title="Stories", stories=stories
    )


# stories of user only
@stories.route("/u/<user>/stories/all")
def all_user_stories(user):
    u = User.query.filter_by(username=user).first_or_404()
    stories = query_all_user_stories(u)

    if u == current_user:
        title = "My Stories"
    else:
        title = u.username + "'s Stories"

    return render_template(
        "dashboard/all_stories.html", dashboard_title=title, stories=stories
    )


# public stories only
@stories.route("/discover/stories/all")
def all_public_stories():
    stories = query_all_public_stories()

    return render_template(
        "dashboard/all_stories.html", dashboard_title="Public Stories", stories=stories
    )

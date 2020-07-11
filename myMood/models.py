from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from myMood import db, login_manager, create_app
from flask import current_app
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)

# DATABASE MODEL
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    acc_image = db.Column(db.String(20), nullable=False, server_default="default.jpg")
    acc_image_bg = db.Column(
        db.String(20), nullable=False, server_default="default.jpg"
    )
    password = db.Column(db.String(60), nullable=False)
    random_say = db.Column(db.Text, nullable=True)
    whoami = db.Column(db.Text, nullable=True)
    social_fb = db.Column(db.String(50), nullable=True)
    social_tw = db.Column(db.String(50), nullable=True)
    social_ig = db.Column(db.String(50), nullable=True)
    social_yt = db.Column(db.String(50), nullable=True)
    posts = db.relationship("Post", backref="author", lazy=True)
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def get_reset_token(self, expires=1800):
        _s = Serializer(current_app.config["SECRET_KEY"], expires)
        return _s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    # User follow system
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # Get the posts of followed users and own
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.date_posted.desc())

    # get user and followed posts with the public posts
    def search_posts(self, query):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(
            Post.content.ilike("%" + query + "%"), followers.c.follower_id == self.id
        )
        own = Post.query.filter(
            Post.content.ilike("%" + query + "%"), Post.user_id == self.id
        )
        public = Post.query.filter(
            Post.content.ilike("%" + query + "%"), Post.state == "public"
        )
        return followed.union(own, public).order_by(Post.date_posted.desc())

    def __repr__(self):
        return f"User('{self.username}', '{self.acc_image}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(12), nullable=False, server_default="default")
    state = db.Column(db.String(8), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}', '{self.date_posted}', '{self.emotion}')"


# DATABASE MODEL

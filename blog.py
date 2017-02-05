import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        temp = jinja_env.get_template(template)
        return temp.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# To create a table/entity, create a class that inherits from db.Model class
# 'Property' in class or entity = columns of table
# In DataStore:
# string < 500 char + indexed
# text > 500 char not indexed
class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Index(Handler):
    """Handles requests coming in to '/' by displaying all posts.
    """
    def render_blog(self, title="", body="", error=""):
        posts = db.GqlQuery("SELECT * FROM Blog "
                                  "ORDER BY created DESC;")
        self.render("blog.html", title=title, body=body, error=error, posts=posts)
    def get(self):
        self.render_blog()

class NewPost(Handler):
    """Handle requests to /new_post form
    """
    def get(self):
        self.render("new_post.html")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if (not title) or (not body) or title.strip()=="" or body.strip()=="":
            error = "A proper post requires both a title and content"
            self.render("new_post.html",title=title, body=body, error=error)
        else:
            new_post = Blog(title=title, body=body)
            # add data to table
            new_post.put()
            self.redirect("/")

class RecentPosts(Handler):
    """Handle requests to /blog by displaying
    5 most recent posts.
    """
    def render_recent(self, title="", body="", error=""):
        posts = db.GqlQuery("SELECT * FROM Blog "
                                  "ORDER BY created DESC "
                                  "LIMIT 5;")
        self.render("blog.html", title=title, body=body, error=error, posts=posts)
    def get(self):
        self.render_recent()

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/new_post', NewPost),
    ('/blog', RecentPosts)
], debug=True)

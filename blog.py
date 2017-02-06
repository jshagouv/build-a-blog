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
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog "
                                  "ORDER BY created DESC;")
        self.render("blog.html", posts=posts)

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
            # create new data entity (row/record)
            new_post = Blog(title=title, body=body)
            # add data to table
            new_post.put()
            # redirect to permalink
            self.redirect("/blog/{0}".format(str(new_post.key().id())))

class RecentPosts(Handler):
    """Handle requests to /blog by displaying
    5 most recent posts.
    """
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog "
                                  "ORDER BY created DESC "
                                  "LIMIT 5;")
        self.render("blog.html",posts=posts)


class ViewPost(Handler):
    """Handle requests to /blog/id, by routing to the permalink
    for the post.
    """
    def get(self, id):
        # get_by_id expects either long or integer; long type better than int
        # for autonumber field.
        post = Blog.get_by_id(long(id))
        error = ""
        if not post:
            error = "No post exists with that ID"
        self.render("single_post.html", post=post, error=error)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/new_post', NewPost),
    ('/blog', RecentPosts),
    # \d = digit, + = at least 1; so requiring an id of 1 or more digits
    webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)

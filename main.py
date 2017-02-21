#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    entry = db.TextProperty(required = True)

    def render(self):
        self._render_text = self.entry.replace('\n', '<br>')
        return render_str("post.html", blog_post = self)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

def render_post (response, post):
    response.out.write(post.title + '<br>')
    response.out.write(post.entry)

class NewPost(Handler):
    """ Handles requests coming in to '/newpost'
        e.g. www.bexblogging.com/newpost
    """
    def render_front(self, title="", entry="", error=""):
        self.render("newpost.html", title = title, entry = entry, error = error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            blog_post = BlogPost(title = title, entry = entry)
            blog_post.put()
            self.redirect("/blog/%s" % str(blog_post.key().id()))
        else:
            error = ("Please enter a title and an entry.")
            self.render_front(title, entry, error)

class MainPage(Handler):
    """ Handles requests coming in to '/blog'
        e.g. www.bexblogging.com/blog
    """
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("blog.html", posts = posts)

class ViewPostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path("BlogPost", int(post_id))
        post = db.get(key)

        if not post:
            error = ("Sorry, there is no blog entry here.")
            return
        else:
            self.render("permalink.html", blog_post = post)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    ('/blog/([0-9]+)', ViewPostHandler)
], debug=True)

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

class blog_post(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    entry = db.TextProperty(required = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class NewPost(Handler):
    """ Handles requests coming in to '/newpost'
        e.g. www.bexblogging.com/newpost
    """
    def render_front(self, title="", entry="", error=""):
        self.render("front.html", title = title, entry = entry, error = error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")
        blog_post = title + entry + created

        if title and entry:
            blog_post_id = self.request.get("blog_post")
            blog_post = blog_post.get_by_id( int(blog_post_id) )
            blog_post.put()
            self.redirect("/blog")
        else:
            error = ("Please enter a title and an entry.")
            self.render_front(title, blog_entry, error)

class MainPage(Handler):
    """ Handles requests coming in to '/blog'
        e.g. www.bexblogging.com/blog
    """
    def get(self):
        blog_post_id = self.request.get("blog_entry")
        blog_post = blog_post.get_by_id( int(blog_post_id) )
        blog_post.put()
        blog_post = db.GqlQuery("SELECT * FROM blog_post ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("blog.html")
        content = t.render(blog_post = blog_post)
        self.response.write(content)

    def post(self):
        blog_post_id = self.request.get("blog_post")
        blog_post = blog_post.get_by_id( int(blog_post_id) )
        blog_post.put()
        blog_entry = db.GqlQuery("SELECT * FROM blog_post ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("blog.html")
        content = t.render(blog_post = blog_post)
        self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        if not id:
            error = ("Sorry, there is no blog entry here.")
        else:
            content = Post.get_by_id
            self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', NewPost),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

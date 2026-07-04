"""Public URLs for CMS blog posts + content pages.

Included from ``apps.cms.urls`` under the same root mount; the URL names
live in the single ``cms`` namespace (e.g. ``cms:blog_list``). Prefixes are configurable via conf.py:

    CMS_POST_URL_PREFIX     (default: "blog") — blog list/detail/category/tag
    CMS_CONTENT_URL_PREFIX  (default: "c")    — content pages
"""

from django.urls import path

from . import conf, views_blog

BLOG = (conf.POST_URL_PREFIX or "blog").strip("/")
CONTENT = (conf.CONTENT_URL_PREFIX or "c").strip("/")

urlpatterns = [
    path(f"{BLOG}/", views_blog.blog_list, name="blog_list"),
    path(f"{BLOG}/category/<slug:slug>/", views_blog.blog_category, name="blog_category"),
    path(f"{BLOG}/tag/<slug:slug>/", views_blog.blog_tag, name="blog_tag"),
    path(f"{BLOG}/<slug:slug>/", views_blog.blog_detail, name="blog_detail"),
    path(f"{CONTENT}/<slug:slug>/", views_blog.content_page, name="content_page"),
]

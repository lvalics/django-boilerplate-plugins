"""Public views for CMS blog posts and content pages.

Reuses the plugin's per-site visibility semantics (site-specific pages beat
all-sites pages on slug collision) and gates posts on ``published_at`` so future
posts 404 until their publication time.
"""

from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from . import conf
from .models import Category, Page, PageType, Tag


def _current_site_id(request):
    """Django Site id for this request when the multi_domain plugin resolved one."""
    site_config = getattr(request, "site_config", None)
    if site_config:
        return site_config.get("site_id")
    return None


def _site_filtered(qs, request):
    """Limit a queryset to pages visible on the current request's site."""
    site_id = _current_site_id(request)
    if site_id:
        return qs.filter(Q(site__isnull=True) | Q(site__site_id=site_id))
    return qs


def _visible_posts(request):
    """Published blog posts visible on the current site, newest first."""
    qs = Page.objects.posts().published()
    qs = _site_filtered(qs, request)
    return qs.select_related("author", "category", "site").prefetch_related("tags").order_by("-published_at")


def _paginate(request, qs):
    paginator = Paginator(qs, conf.POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get("page", 1))


def _render_list(request, qs, title, kind, **extra):
    page_obj = _paginate(request, qs)
    context = {
        "base_template": conf.BASE_TEMPLATE,
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "archive_title": title,
        "archive_kind": kind,
    }
    context.update(extra)
    return render(request, "cms/blog/list.html", context)


def blog_list(request):
    return _render_list(request, _visible_posts(request), "Blog", "all")


def blog_detail(request, slug):
    site_id = _current_site_id(request)
    post = (
        _visible_posts(request)
        .filter(slug=slug)
        .order_by(F("site_id").asc(nulls_last=True), "-published_at")
        .first()
    )
    if post is None:
        raise Http404("Post not found")

    # Defense in depth: a site-scoped post must only be served on its site.
    if post.site and site_id and post.site.site_id != site_id:
        raise Http404("Post not found")

    related = []
    if post.category_id:
        related = list(_visible_posts(request).filter(category=post.category).exclude(pk=post.pk)[:3])

    return render(
        request,
        "cms/blog/detail.html",
        {"base_template": conf.BASE_TEMPLATE, "post": post, "related": related},
    )


def blog_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    qs = _visible_posts(request).filter(category=category)
    return _render_list(request, qs, f"Category: {category.name}", "category", category=category)


def blog_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    qs = _visible_posts(request).filter(tags=tag)
    return _render_list(request, qs, f"Tag: {tag.name}", "tag", tag=tag)


def content_page(request, slug):
    site_id = _current_site_id(request)
    page = (
        _site_filtered(Page.objects.content_pages().filter(is_active=True), request)
        .select_related("site")
        .prefetch_related("zones")
        .filter(slug=slug)
        .order_by(F("site_id").asc(nulls_last=True), "-created_at")
        .first()
    )
    if page is None:
        raise Http404("Page not found")

    if page.site and site_id and page.site.site_id != site_id:
        raise Http404("Page not found")

    return render(
        request,
        "cms/content_page.html",
        {"base_template": conf.BASE_TEMPLATE, "page": page},
    )

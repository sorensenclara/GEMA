from django import template

from core.utils.pagination import ALLOWED_PAGE_SIZES, get_page_number_window

register = template.Library()


@register.filter
def page_number_window(page_obj, window=10):
    """Up to `window` page numbers centered on the current page -- used by
    _pagination.html to render a sliding block of page links instead of just
    prev/next."""
    return get_page_number_window(page_obj.number, page_obj.paginator.num_pages, window)


@register.simple_tag
def allowed_page_sizes():
    """The project-wide allowed page sizes (core/utils/pagination.py), exposed
    to templates so the page-size selector doesn't hardcode a second copy of
    the list."""
    return ALLOWED_PAGE_SIZES

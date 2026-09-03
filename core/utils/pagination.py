from django.core.paginator import Paginator

DEFAULT_PAGE_SIZE = 20
ALLOWED_PAGE_SIZES = [10, 20, 50, 100]


def get_page_size(request):
    size = request.GET.get("page_size")
    if size and size.isdigit() and int(size) in ALLOWED_PAGE_SIZES:
        return int(size)
    return DEFAULT_PAGE_SIZE


def paginate(queryset, request):
    page_size = get_page_size(request)
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get("page", 1))


def get_page_number_window(current_page, num_pages, window=10):
    """Up to `window` page numbers centered on current_page, clamped to
    [1, num_pages] -- slides as current_page changes, always returns exactly
    `window` numbers once num_pages exceeds it."""
    if num_pages <= window:
        return list(range(1, num_pages + 1))

    half = window // 2
    start = current_page - half
    end = start + window - 1

    if start < 1:
        start = 1
        end = window
    if end > num_pages:
        end = num_pages
        start = end - window + 1

    return list(range(start, end + 1))

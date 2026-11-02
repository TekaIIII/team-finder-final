from django.core.paginator import Paginator

from .constants import PAGE_SIZE


def paginate_queryset(queryset, request, page_size=PAGE_SIZE):
    """Разбивает список на страницы, сохраняя параметры фильтра."""
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_prefix = query_params.urlencode()
    if query_prefix:
        query_prefix += "&"
    return page, query_prefix

from django.core.paginator import Paginator

NA_STR = 12


def razbit(qs, zap):
    """Получает страницу и сохраняет параметры фильтра без старого page."""
    pgn = Paginator(qs, NA_STR)
    stran = pgn.get_page(zap.GET.get("page"))
    filtr = zap.GET.copy()
    filtr.pop("page", None)
    pref = filtr.urlencode()
    if pref:
        pref += "&"
    return stran, pref

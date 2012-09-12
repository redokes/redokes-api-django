from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_paged_set(query_set, limit=10, page=1):
    paginator = Paginator(query_set, limit)
    try:
        query_set = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        query_set = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        query_set = paginator.page(page)
    
    return query_set
from typing import Dict
from django.core.paginator import Paginator, EmptyPage
from rest_framework.exceptions import ValidationError


def paginate(data, pagenumber, page_size):
    paginator = Paginator(data, page_size)
    if int(pagenumber) > paginator.num_pages:
        raise ValidationError("Not enough pages", code=404)

    try:
        previous_page_number = paginator.page(pagenumber).previous_page_number()
    except EmptyPage:
        previous_page_number = None

    try:
        next_page_number = paginator.page(pagenumber).next_page_number()
    except EmptyPage:
        next_page_number = None

    return {
        'pagination': {
            'previous_page': previous_page_number,
            'is_previous_page': paginator.page(pagenumber).has_previous(),
            'next_page': next_page_number,
            'is_next_page': paginator.page(pagenumber).has_next(),
            'start_index': paginator.page(pagenumber).start_index(),
            'end_index': paginator.page(pagenumber).end_index(),
            'total_entries': paginator.count,
            'total_pages': paginator.num_pages,
            'page': int(pagenumber)
        },
        'results': paginator.page(pagenumber).object_list
    }

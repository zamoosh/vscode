from django.db import transaction
from book.models import Book, Catalogue, Lang
from colorful_logging import c_print
import datetime
import pytz


def __action__():
    catalogues: list[str] = [
        "حکمت‌ها", "خطبه‌ها", "نامه‌ها"
    ]
    now = datetime.datetime.now().replace(tzinfo=pytz.UTC)

    try:
        with transaction.atomic():
            lang = Lang()
            lang.name = "فارسی"
            lang.save()

            b = Book()
            b.title = "نهج‌البلاغه دشتی"
            b.subject = "دینی"
            b.writer = "امام علی (ع)"
            b.editor = "آقای دشتی"
            b.standard_number = ""
            b.lang_id = 1
            b.publisher = "Nahser"
            b.page_count = 4590
            b.cover_count = 3
            b.cover_number = 1
            b.view_type = Book.DEDICATED
            b.publish_date = now
            b.save()

            for item in catalogues:  # type: str
                cat = Catalogue()
                cat.name = item
                cat.book_id = b.id
                cat.order = 0
                cat.save()

    except Exception as e:
        c_print(e, "red")


if __name__ == '__main__':
    __action__()
    c_print("STARTERS BOOK AND CATALOGUES ADDED", "gree")

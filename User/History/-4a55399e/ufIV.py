from django.test import TestCase
from book.models import Book, Lang, Catalogue, Content
from book.api.book_api import BookApi
from rest_framework.test import APIRequestFactory, RequestsClient
from rest_framework.response import Response
from rest_framework.request import Request
from colorful_logging import color_print
import random
import math


class BookTestCase(TestCase):

    def setUp(self):
        lang = Lang.objects.create(name="FA")
        color_print("Lang created", "green")

        book = Book()
        book.title = 'How to become a man!'
        book.category = "sample category 1"
        book.writer = "hamed azim"
        book.editor = None
        book.lang = lang
        book.save()
        color_print("Book created", "green")

        cat_to_be_create: list[Catalogue] = []
        for i in range(5):
            catalogue = Catalogue()
            catalogue.book = book
            catalogue.name = f'SEASON--{i + 1}'
            cat_to_be_create.append(catalogue)
        Catalogue.objects.bulk_create(cat_to_be_create, batch_size=len(cat_to_be_create))
        color_print("Catalogues created", "green")

        bc_to_be_create: list[Content] = []
        i = 1
        while i <= 5000:
            bc = Content()
            bc.catalogue = random.choice(cat_to_be_create)
            bc.body = f'body {i}'
            bc.page_number = math.ceil(i / 10)
            bc_to_be_create.append(bc)
            i += 1
        Content.objects.bulk_create(bc_to_be_create, batch_size=len(bc_to_be_create))
        color_print("Book Contents created", "green")

        return

    def test_book_create(self):
        factory = APIRequestFactory()
        request: Request = factory.get('/api/book/')
        view = BookApi.as_view({'get': 'list'})
        response: Response = view(request)
        print(response.data['results'])

        return

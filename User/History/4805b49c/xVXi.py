import re
import pandas as pd
from pandas import DataFrame
from pandas.core.series import Series
from typing import Iterable, Any
from colorful_logging import c_print
from django.apps import apps
from django.db.models import Model
from translate.models import (
    Book,
    Catalogue,
    Content,
    BookTranslate,
    CatalogueTranslate,
    ContentTranslate,
)


class Parser:
    pattern = re.compile(r"\d+")
    en = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    fa = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"]
    ar = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"]

    @classmethod
    def to_other_numerics(cls, s: str, numeric_list=None) -> str:
        if numeric_list is None:
            numeric_list = cls.ar
        for ch in s:
            if ch in cls.en:
                s = s.replace(ch, numeric_list[cls.en.index(ch)])

        return s

    @staticmethod
    def parser(
            xls: pd.ExcelFile,
            book: Book | BookTranslate,
            parent_catalogue: Catalogue | CatalogueTranslate,
            lead_catalogue_name: str,
            catalogue_model: Model,
            content_model: Model,
            starter_column: int = 3,
            main_catalogue: bool = False,
            main_content: bool = False
    ):
        """
        Parameters
        ----------
        xls: pd.ExcelFile
        book: Book | BookTranslate
        parent_catalogue: Catalogue | CatalogueTranslate
        lead_catalogue_name: str
            - the name in which used to populate tables
        catalogue_model: Catalogue | CatalogueTranslate
        content_model: Content | ContentTranslate
            - pointer to model class
        starter_column: int
            - 3 is for ARABIC
            - 4 is for PERSIAN
        main_catalogue: bool
            - true: get the main "Catalogue" based on the sheet name
            - false: do nothing
        main_content: bool
            - just like "main_catalogue"
        """

        if not (starter_column == 3 or starter_column == 4):
            raise ValueError("'starter_column' must be selected of: {3, 4}.")

        numeric_sys = Parser.ar
        if starter_column == 3:
            numeric_sys = Parser.ar
        elif starter_column == 4:
            numeric_sys = Parser.fa

        for sheet_name in xls.sheet_names:  # type: str
            c_print(f"sheet number: {sheet_name}", "cyan")

            df: "DataFrame" = xls.parse(sheet_name, header=None)

            number = Parser.pattern.findall(sheet_name)

            catalogue_name: str = f"{lead_catalogue_name} " f"{Parser.to_other_numerics(number[0], numeric_sys)}: "

            original_catalogue = None
            original_catalogue_name: str = ""
            if lead_catalogue_name == "حکمت":
                original_catalogue_name: str = f"الحكمة " f"{Parser.to_other_numerics(number[0], Parser.ar)}: "
            elif lead_catalogue_name == "خطبه‌ی":
                original_catalogue_name: str = f"خطبة " f"{Parser.to_other_numerics(number[0], Parser.ar)}: "
            elif lead_catalogue_name == "نامه‌ی":
                original_catalogue_name: str = f"الحرف " f"{Parser.to_other_numerics(number[0], Parser.ar)}: "

            original_content = None
            original_content_body: str = ""

            catalogue = catalogue_model()
            catalogue.parent = parent_catalogue
            catalogue.book = book
            catalogue.order = 0

            for row in df.itertuples():
            # for row in df.iterrows():  # type: Iterable[tuple[Any, Series]]

                page_number = None
                try:
                    page_number = int(row[-1])
                except ValueError:
                    page_number = None
                # c_print(f"finally page number is: {page_number}", "underline")

                content = content_model()
                content.catalogue = catalogue
                content.body = ""
                content.page_number = page_number
                content.order = 0
                content_body = ""

                for col in range(len(row)):  # type: int
                    # === SKIP THE EMPTY OR NOT ACCEPTABLE CELLS === #
                    conditions = [
                        col == 0,
                        str(row[col]) == "nan",
                        str(row[col]).lower() == "x",
                        len(str(row[col]).strip()) <= 0
                    ]
                    if any(conditions):
                        # c_print(
                        #     f"skip: xls: {xls} | sheet number: {sheet_name} | starter col: {starter_column}", "yellow"
                        # )
                        if col == 1 or col == 2:
                            continue
                    # === END SKIP THE EMPTY OR NOT ACCEPTABLE CELLS === #

                    # === ADD "Catalogue" NAME === #
                    if col == 1 and row[0] == 0:
                        if main_catalogue:
                            original_catalogue_name += str(row[col]).strip()

                            original_catalogue = Catalogue.objects.get(
                                name=original_catalogue_name
                            )

                        catalogue_name += str(row[col].strip())
                        catalogue.name = catalogue_name
                        catalogue.start_page = page_number
                        catalogue.catalogue = original_catalogue
                        catalogue.save()

                        content.catalogue = catalogue
                    # === END Add "Catalogue" name here === #

                    if int(sheet_name) == 99:
                        print("ali ali ali")

                    # === CREATE "Content" === #
                    if col == starter_column:  # 3

                        if main_content:
                            original_content_body += f"<h2>{row[3].strip()}</h2>\n\n"

                        content_body += f"<h2>{row[col].strip()}</h2>\n\n"

                    if col == starter_column + 2:  # 5
                        if main_content:
                            original_content_body += row[5].strip()

                            c_print(original_content_body, 'gray')

                            if int(sheet_name) == 99:
                                print("ali ali ali")
                            original_content = Content.objects.get(
                                body=original_content_body
                            )

                        content_body += row[col].strip()
                        content.body = content_body
                        content.content = original_content
                        content.save()

                    if col == starter_column + 4:  # 7
                        if main_content:
                            original_content = Content.objects.get(
                                body=row[7]
                            )

                        new_content = content_model()
                        new_content.catalogue = catalogue
                        new_content.page_number = page_number
                        new_content.body = row[col]
                        new_content.order = 0
                        new_content.content = original_content
                        new_content.save()
                    # === END CREATE "Content" === #

                # === RESET ORIGINAL CONTENT BODY === #
                original_content_body = ""
                # === END RESET ORIGINAL CONTENT BODY === #

        return

    @staticmethod
    def __action__():
        Parser.parse_Khotbeh_ar()
        Parser.parse_hekmat_ar()
        Parser.parse_nameh_ar()

        # Parser.parse_khotbeh_fa()
        # Parser.parse_hekmat_fa()
        # Parser.parse_nameh_fa()

        c_print("ALL DATA POPULATED IN DB!", "green")

        return

    @staticmethod
    def parse_nameh_ar():
        book = Book.objects.get(deleted_at=None, title="نهج‌البلاغه دشتی عربی")
        parent = Catalogue.objects.get(name="الحروف")
        content_model = apps.get_model('book', 'content')
        catalogue_model = apps.get_model('book', 'catalogue')

        with pd.ExcelFile("/home/zamoosh/Downloads/nameh.xlsx") as xls:  # type: pd.ExcelFile
            Parser.parser(
                xls, book, parent, "الحرف", catalogue_model=catalogue_model, content_model=content_model,
                starter_column=3, main_catalogue=False
            )

            xls.close()

        c_print("ALL NAMEHs ADDED", "green")
        return

    @staticmethod
    def parse_Khotbeh_ar():
        book = Book.objects.get(deleted_at=None, title="نهج‌البلاغه دشتی عربی")
        parent = Catalogue.objects.get(name="الخطب")
        content_model = apps.get_model('book', 'content')
        catalogue_model = apps.get_model('book', 'catalogue')

        with pd.ExcelFile("/home/zamoosh/Downloads/khotbeh.xlsx") as xls:  # type: pd.ExcelFile
            Parser.parser(
                xls, book, parent, "خطبة", catalogue_model=catalogue_model, content_model=content_model,
                starter_column=3, main_catalogue=False
            )

            xls.close()

        c_print("ALL KHOTBEHs ADDED", "green")
        return

    @staticmethod
    def parse_hekmat_ar():
        book = Book.objects.get(deleted_at=None, title="نهج‌البلاغه دشتی عربی")
        parent = Catalogue.objects.get(name="حكمة")
        content_model = apps.get_model('book', 'content')
        catalogue_model = apps.get_model('book', 'catalogue')

        with pd.ExcelFile("/home/zamoosh/Downloads/hekmat.xlsx") as xls:  # type: pd.ExcelFile
            Parser.parser(
                xls, book, parent, "الحكمة", catalogue_model=catalogue_model, content_model=content_model,
                starter_column=3, main_catalogue=False
            )

            xls.close()

        c_print("ALL HEKMATs ADDED", "green")
        return

    @staticmethod
    def parse_nameh_fa():
        book = BookTranslate.objects.get(deleted_at=None, title="نهج‌البلاغه دشتی فارسی")
        parent = CatalogueTranslate.objects.get(name="نامه‌ها")
        content_model = apps.get_model('translate', 'contenttranslate')
        catalogue_model = apps.get_model('translate', 'cataloguetranslate')
        # content_model = ContentTranslate
        # catalogue_model = CatalogueTranslate

        with pd.ExcelFile("/home/zamoosh/Downloads/nameh.xlsx") as xls:  # type: pd.ExcelFile
            Parser.parser(
                xls, book, parent, "نامه‌ی", catalogue_model=catalogue_model, content_model=content_model,
                starter_column=4, main_catalogue=True, main_content=True
            )

            xls.close()

        c_print("ALL PERSIAN NAMEH ADDED", "green")
        return

    @staticmethod
    def parse_khotbeh_fa():
        book = BookTranslate.objects.get(deleted_at=None, title="نهج‌البلاغه دشتی فارسی")
        parent = CatalogueTranslate.objects.get(name="خطبه‌ها")
        content_model = apps.get_model('translate', 'contenttranslate')
        catalogue_model = apps.get_model('translate', 'cataloguetranslate')
        # content_model = ContentTranslate
        # catalogue_model = CatalogueTranslate

        with pd.ExcelFile("/home/zamoosh/Downloads/khotbeh.xlsx") as xls:  # type: pd.ExcelFile
            Parser.parser(
                xls, book, parent, "خطبه‌ی", catalogue_model=catalogue_model, content_model=content_model,
                starter_column=4, main_catalogue=True, main_content=True
            )

            xls.close()

        c_print("ALL PERSIAN KHOTBEH ADDED", "green")
        return

    @staticmethod
    def parse_hekmat_fa():
        book = BookTranslate.objects.get(deleted_at=None, title="نهج‌البلاغه دشتی فارسی")
        parent = CatalogueTranslate.objects.get(name="حکمت‌ها")
        content_model = apps.get_model('translate', 'contenttranslate')
        catalogue_model = apps.get_model('translate', 'cataloguetranslate')
        # content_model = ContentTranslate
        # catalogue_model = CatalogueTranslate

        with pd.ExcelFile("/home/zamoosh/Downloads/hekmat.xlsx") as xls:  # type: pd.ExcelFile
            Parser.parser(
                xls, book, parent, "حکمت", catalogue_model=catalogue_model, content_model=content_model,
                starter_column=4, main_catalogue=True, main_content=True
            )

            xls.close()

        c_print("ALL PERSIAN HEKMAT ADDED", "green")
        return

import re
import pandas as pd
from pandas import DataFrame
from colorful_logging import c_print
from translate.models import (
    Book,
    Catalogue,
    Content,
    BookTranslate,
    CatalogueTranslate,
    ContentTranslate,
)

pattern = re.compile(r"\d+")
max_catalogue_name = 0

en = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
fa = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"]
ar = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"]


def to_other_numerics(s: str, numeric_list=None) -> str:
    if numeric_list is None:
        numeric_list = ar
    for ch in s:
        if ch in en:
            s = s.replace(ch, numeric_list[en.index(ch)])

    return s


def add_khotbeh():
    global max_catalogue_name

    book = Book.objects.filter(deleted_at=None).first()
    khotbeh = Catalogue.objects.get(name="حکمت‌ها")

    contents_to_be_added: list[Content] = []

    with pd.ExcelFile("/home/zamoosh/Downloads/hekmat.xlsx") as xls:
        for sheet_name in xls.sheet_names:  # type: str
            df: "DataFrame" = xls.parse(sheet_name, header=None)

            number = pattern.findall(sheet_name)

            catalogue_name: str = f"حکمت " f"{to_other_numerics(number[0], ar)}: "

            catalogue = Catalogue()
            catalogue.parent = khotbeh
            catalogue.book = book
            catalogue.order = 0

            for row in df.itertuples():

                page_number = None
                try:
                    page_number = int(row[-1])
                except ValueError:
                    page_number = None
                c_print(f"finally page number is: {page_number}", "underline")

                content = Content()
                content.catalogue = catalogue
                content.body = ""
                content.page_number = page_number
                content.order = 0
                content_body = ""

                for col in range(len(row)):  # type: int
                    if col == 0:
                        continue

                    # === Add "Catalogue" name here === #
                    if row[0] == 0 and col == 1:
                        catalogue_name += f"{row[col].strip()}"
                        if len(catalogue_name) > max_catalogue_name:
                            max_catalogue_name = len(catalogue_name)
                        catalogue.name = catalogue_name
                        catalogue.start_page = page_number
                        print(max_catalogue_name, sheet_name)
                        catalogue.save()
                        content.catalogue = catalogue

                    if str(row[col]) == "nan" or str(row[col]).lower() == "x":
                        continue

                    # === Create "Content" === #
                    if col == 3 and len(str(row[col]).strip()) > 0:
                        content_body += f"<h2>{row[col].strip()}</h2>\n\n"

                    if col == 5 and len(str(row[col]).strip()) > 0:
                        content_body += row[col].strip()
                        # c_print(content_body, "dark cyan")
                        # c_print(page_number, row, "dark red")
                        # c_print(row[col], "dark yellow")
                        content.body = content_body
                        content.save()

                    if col == 7:
                        new_content = Content()
                        new_content.catalogue = catalogue
                        new_content.page_number = page_number
                        new_content.body = row[col]
                        new_content.order = 0
                        new_content.save()

    return


def __action__():
    add_khotbeh()

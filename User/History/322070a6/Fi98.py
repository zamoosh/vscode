import re
import pandas as pd
from pandas import DataFrame
from colorful_logging import c_print
from book.models import Book, Catalogue, Content

pattern = re.compile(r"\d+")

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


def __action__():
    book = Book.objects.filter(deleted_at=None).first()
    khotbeh = Catalogue.objects.get(name="خطبه‌ها")

    with pd.ExcelFile('/home/zamoosh/aalulbayt/makarem/khotbe-paged.xlsx') as xls:
        max_cols: int = 0
        max_cols_name: str = ""

        for sheet_name in xls.sheet_names:  # type: str
            df: "DataFrame" = xls.parse(sheet_name, header=None)

            number = pattern.findall(sheet_name)
            catalogue_name: str = (
                f"خطبه‌ی "
                f"{to_other_numerics(number[0], ar)}: "
            )

            if len(number) > 0:
                for row in df.itertuples():
                    if len(row) - 1 > max_cols:
                        max_cols = len(row) - 1
                        max_cols_name = row[1]
                    for c in range(len(row)):  # type: int

                        if c == 0:
                            continue

                        if row[0] == 0 and c == 1:
                            catalogue_name += f"{row[1].strip()}"

        c_print(max_cols, "bold")
        c_print(max_cols_name, "bold")

    return

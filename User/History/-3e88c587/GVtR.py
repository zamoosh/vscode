import pandas as pd


def main():
    with pd.ExcelFile("/home/zamoosh/Downloads/khotbeh.xlsx") as xls:
        df: pd.DataFrame = xls.parse("193", header=None)
        for row in df.itertuples():

            for col in range(len(row)):  # type: int

                content: str = row[col]
                if content.strip() == "x":
                    print(col, type(content))


if __name__ == "__main__":
    main()

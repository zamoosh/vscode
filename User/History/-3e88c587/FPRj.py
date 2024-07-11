import pandas as pd


def main():
    with pd.ExcelFile("/home/zamoosh/Downloads/khotbeh.xlsx") as xls:
        df: pd.DataFrame = xls.parse("193", header=None)
        for row in df.itertuples():

            if row[0] == 0:
                continue

            for col in range(len(row)):  # type: int

                content: str = row[col]
                if content == "x" or type(content) == int:
                    print("row: ", row[0])
                    print("col: ", col)

                    print("\n===\n")

                    print(col, content)


if __name__ == "__main__":
    main()

import pandas as pd


def main():
    with pd.ExcelFile("/home/zamoosh/Downloads/khotbeh.xlsx") as xls:
        df: pd.DataFrame = xls.parse("193", header=None)
        for row in df.itertuples():


if __name__ == "__main__":
    main()

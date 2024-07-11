import pandas as pd


def main():
    with pd.ExcelFile("/home/zamoosh/Downloads/khotbeh.xlsx") as df:
        df.parse("193", header=None)


if __name__ == "__main__":
    main()

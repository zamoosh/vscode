import pandas as pd


def main():
    df: pd.DataFrame = pd.read_excel("/home/zamoosh/Downloads/khotbeh.xlsx")

    print(df.describe())
    print(df.info())


if __name__ == "__main__":
    main()

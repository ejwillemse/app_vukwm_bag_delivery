import pandas as pd


def process_excel(file_name):
    return pd.read_excel(file_name)


if __name__ == "__main__":
    filename = "data/test/elias_test.xlsx"
    df = process_excel(filename)
    print(df)

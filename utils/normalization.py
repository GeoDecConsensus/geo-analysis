import pandas as pd


class Normalization:

    @staticmethod
    def normalize_columns(df):
        required_columns = ["GDI", "stake_weight"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"'{col}' column is missing. Both 'GDI' and 'stake_weight' columns are required.")

        # Normalize 'GDI'
        total_gdi = df["GDI"].sum()
        df["GDI"] = df["GDI"] / total_gdi

        # Normalize 'stake_weight'
        total_stake_weight = df["stake_weight"].sum()
        df["stake_weight"] = df["stake_weight"] / total_stake_weight

        return df

    @staticmethod
    def normalize_column(df, col):
        if col not in df.columns:
            raise ValueError(f"'{col}' column is missing. Both 'GDI' and 'stake_weight' columns are required.")

        df[col] = df[col] / df[col].sum()

        return df

    @staticmethod
    def normalize_columnToInteger(df, col):
        if col not in df.columns:
            raise ValueError(f"'{col}' column is missing. Both 'GDI' and 'stake_weight' columns are required.")

        # Normalize and convert to integers element-wise
        df[col] = (df[col] / df[col].sum() * pow(10, 6)).astype(int)

        return df


# # Example usage
# df = pd.read_csv('data/pre_processed_data/sui.csv')
# print(df.head())
# df = Normalization.normalize_column(df, 'GDI')
# df = Normalization.normalize_columnToInteger(df,'stake_weight')
# print(df.head())

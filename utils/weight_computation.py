import pandas as pd

from utils.normalization import Normalization


class WeightComputation:
    def __init__(self, df):
        """
        Initialize the WeightComputation class with a pandas DataFrame.

        :param df: A pandas DataFrame with 'stake_weight' and 'GDI' columns.
        """
        self.df = df

    def compute_linear_weight(self, lambdas=[0.9, 0.8, 0.7, 0.6, 0.5]):
        """
        Compute lambda * stake_weight + (1 - lambda) * GDI and add as new columns.

        :param lambdas: List of lambda values for linear weighting.
        """
        for lam in lambdas:
            column_name = f"{lam}linear_weight"
            self.df[column_name] = lam * self.df["stake_weight"] + (1 - lam) * self.df["GDI"]

    def compute_exponential_weight(self, alphas=[0.9, 0.8, 0.7, 0.6, 0.5]):
        """
        Compute (stake_weight^alpha) * (GDI^(1 - alpha)) and add as new columns.

        :param alphas: List of alpha values for exponential weighting.
        """
        for alpha in alphas:
            column_name = f"{alpha}exponential_weight"
            self.df[column_name] = (self.df["stake_weight"] ** alpha) * (self.df["GDI"] ** (1 - alpha))

    def get_updated_df(self):
        """
        Return the DataFrame after computing the weights.

        :return: Updated DataFrame.
        """
        # Use self.df instead of df
        self.df = Normalization.normalize_column(self.df, col="stake_weight")
        self.df = Normalization.normalize_column(self.df, col="GDI")
        print(self.df.head())

        # Calculate weights
        self.compute_linear_weight()
        # self.compute_exponential_weight()

        # self.df = Normalization.normalize_columnToInteger(self.df, col="stake_weight")

        return self.df


# USAGE
# wc = WeightComputation(df)
# df = wc.get_updated_df()
# print(df.head())

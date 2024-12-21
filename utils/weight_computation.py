import pandas as pd

from utils.normalization import Normalization


class WeightComputation:
    def __init__(self, df):
        """
        Initialize the WeightComputation class with a pandas DataFrame.

        :param df: A pandas DataFrame with 'stake_weight' and 'GDI' columns.
        """
        self.df = df

    def compute_linear_weight(self, lambdas=[0.8, 0.6, 0.4, 0.2, 0]):
        """
        Compute lambda * stake_weight + (1 - lambda) * GDI and add as new columns.

        :param lambdas: List of lambda values for linear weighting.
        """
        for i in lambdas:
            column_name = f"{i}linear_weight"
            self.df[column_name] = i * self.df["stake_weight"] + (1 - i) * self.df["GDI"]

    def compute_exponential_weight(self, alphas=[0.8, 0.6, 0.4, 0.2, 0]):
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


#### USED THIS To GENERATE FILES IN data/wc
# def get_all_files(folder_path):
#     """Returns a list of all CSV files in the specified folder."""
#     return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]


# files = get_all_files('data/pre_processed_data/')
# output_folder = 'data/wc/'
# for file in files:
#     df = pd.read_csv(f'data/pre_processed_data/{file}')
#     print(f'File: {file}')
#     wc = WeightComputation(df)
#     df =wc.get_updated_df()    
#     # Save the data to CSV
#     output_file_path = os.path.join(output_folder, file)
#     df.to_csv(output_file_path, index=False)
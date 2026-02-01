"""Exploratory Data Analysis (EDA) Template."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def perform_eda(df: pd.DataFrame):
    """Run a standard exploratory analysis.

    Args:
        df: The pandas DataFrame to analyze.

    """
    # 1. Descriptive Statistics
    print("\n--- Descriptive Statistics ---")
    print(df.describe())

    # 2. Correlation Matrix
    numeric_df = df.select_dtypes(include=["number"])
    if not numeric_df.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Matrix")
        plt.show()

    # 3. Distribution of Key Variables
    # Example: Select first 3 numeric columns
    cols_to_plot = numeric_df.columns[:3]
    for col in cols_to_plot:
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col], kde=True)
        plt.title(f"Distribution of {col}")
        plt.show()


if __name__ == "__main__":
    # Example usage with dummy data
    import numpy as np

    data = pd.DataFrame(
        {
            "feature_a": np.random.randn(100),
            "feature_b": np.random.randn(100) * 2 + 5,
            "target": np.random.randint(0, 2, 100),
        }
    )
    perform_eda(data)

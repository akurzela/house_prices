from sys import modules

from pandas import DataFrame


def apply_preprocessor(df: DataFrame, query: str):
    """Preprocess dataset (functions should be named 'preprocess_<query>')"""

    try:
        df = getattr(modules[__name__], f"preprocess_{query}")(df)
    except AttributeError:
        return df

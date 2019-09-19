from sys import modules

import pandas as pd
from warnings import warn


def apply_preprocessor(df: pd.DataFrame, query: str):
    """Preprocess dataset (functions should be named 'preprocess_<query>')"""

    try:
        f = getattr(modules[__name__], f"preprocess_{query}")
    except AttributeError:
        warn(f"No preprocessor found with name preprocess_{query}")
        f = lambda x: x

    return f(df)


def preprocess_nvf(df: pd.DataFrame):
    return df[df["metric_date"] > "2017-06-01"]

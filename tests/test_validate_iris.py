import pytest
from sklearn.datasets import load_iris
from iris_project.transformers import validate_iris


def test_clean_iris_passes():
    df = load_iris(as_frame=True).frame
    out = validate_iris.validate(df)
    validate_iris.test_output(out)     # raises AssertionError if the data is bad


def test_missing_value_is_caught():
    df = load_iris(as_frame=True).frame
    df.iloc[0, 0] = None
    with pytest.raises(AssertionError):
        validate_iris.test_output(validate_iris.validate(df))

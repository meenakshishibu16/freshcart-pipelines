if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ImportError:
        def transformer(func):
            return func
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(func):
            return func


# C4 (my own block): sits between load_iris and prepare_data.
# It passes the table through unchanged and reports how many missing values and classes it saw.
@transformer
def validate(df, *args, **kwargs):
    print('Missing values:', int(df.isna().sum().sum()), '| Classes:', df['target'].nunique())
    return df


# The gate for this block: no missing values and exactly 3 classes.
# If either fails, prepare_data and everything after it never run.
@test
def test_output(output, *args):
    assert output.isna().sum().sum() == 0, 'Iris must have no missing values'
    assert output['target'].nunique() == 3, 'Iris must have exactly 3 classes'

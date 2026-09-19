from unittest.mock import patch

from hog_uploader.decorators import time_function


@patch("hog_uploader.decorators.perf_counter")
def test_time_function(mock_perf_counter, capsys):
    # given
    mock_perf_counter.side_effect = [1, 2]

    @time_function
    def some_function():
        pass

    # when
    some_function()

    # then
    actual = capsys.readouterr().out
    expected = "function some_function ran in 1.00 seconds\n"

    assert actual == expected

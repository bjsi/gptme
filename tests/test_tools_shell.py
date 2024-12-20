from gptme.tools.shell import _shorten_stdout


def test_shorten_stdout_timestamp():
    s = """2021-09-02T08:48:43.123Z
2021-09-02T08:48:43.123Z
"""
    assert _shorten_stdout(s, strip_dates=True) == "\n\n"


def test_shorten_stdout_common_prefix():
    s = """foo 1
foo 2
foo 3
foo 4
foo 5"""
    assert _shorten_stdout(s, strip_common_prefix_lines=5) == "1\n2\n3\n4\n5"


def test_shorten_stdout_indent():
    # check that indentation is preserved
    s = """
l1 without indent
    l2 with indent
""".strip()
    assert _shorten_stdout(s) == s


def test_shorten_stdout_blanklines():
    s = """l1

l2"""
    assert _shorten_stdout(s) == s


def test_shorten_stdout_git_commit():
    s = """[issue d620de9] test
 1 file changed, 1 insertion(+), 1 deletion(-)"""
    assert _shorten_stdout(s) == s
    
    # Verify that date stripping doesn't affect git commit messages
    assert _shorten_stdout(s, strip_dates=True) == s
    
    # Test with a mix of dates and commit messages
    s2 = """[issue d620de9] test
2024-03-20T15:30:45.123Z Some change
 1 file changed, 1 insertion(+), 1 deletion(-)"""
    expected = """[issue d620de9] test
 Some change
 1 file changed, 1 insertion(+), 1 deletion(-)"""
    assert _shorten_stdout(s2, strip_dates=True) == expected
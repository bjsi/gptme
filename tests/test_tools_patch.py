from gptme.tools.patch import patch

def test_patch_edge_cases(temp_file):
    content = """line1
line2
line3
line4"""

    # Test (-1, -1) - should append to end of file
    with temp_file(content) as f:
        messages = list(patch(f, (-1, -1), "new_line"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == content + "\nnew_line"
        assert any("Updated region" in msg.content for msg in messages)

    # Test (0, -1) - should replace entire file
    with temp_file(content) as f:
        list(patch(f, (0, -1), "replacement"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == "replacement"

    # Test (1, 1) - should replace just first line
    with temp_file(content) as f:
        list(patch(f, (1, 1), "new_first_line"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """new_first_line
line2
line3
line4"""

    # Test (1, -1) - should replace from line 1 to end
    with temp_file(content) as f:
        list(patch(f, (1, -1), "new_content"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == "new_content"


def test_patch_empty_file(temp_file):
    # Test patching an empty file
    with temp_file("") as f:
        list(patch(f, (1, 1), "new content"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == "new content"


def test_patch_multiple_lines_into_single_line(temp_file):
    content = "line1\nline2\nline3"
    with temp_file(content) as f:
        list(patch(f, (2, 2), "new_line\nnew_line2\nnew_line3"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == "line1\nnew_line\nnew_line2\nnew_line3\nline3"


def test_patch_beyond_file_length(temp_file):
    content = "single line"
    # Test patching beyond file length
    with temp_file(content) as f:
        list(patch(f, (100, 100), "appended line"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == content + "\nappended line"


def test_patch_multiline_replacement(temp_file):
    content = """line1
line2
line3
line4"""
    new_content = """new1
new2"""
    
    # Test replacing middle lines
    with temp_file(content) as f:
        list(patch(f, (2, 3), new_content))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1
new1
new2
line4"""


def test_patch_create_new_file(tmp_path):
    new_file = tmp_path / "new_file.txt"
    content = "new file content"
    
    # Test creating a new file with patch
    list(patch(new_file, (1, 1), content))
    assert new_file.exists()
    assert new_file.read_text() == content


def test_patch_preserve_trailing_newline(temp_file):
    content = "line1\nline2\n"  # Note trailing newline
    with temp_file(content) as f:
        list(patch(f, (2, 2), "new_line"))
        with open(f, encoding="utf-8") as f:
            result = f.read()
            assert result == "line1\nnew_line\n"
            assert result.endswith("\n")


def test_patch_messages(temp_file):
    """Test that patch returns appropriate messages"""
    with temp_file("original") as f:
        messages = list(patch(f, (1, 1), "new content"))
        
        # Should have at least one message showing the updated region
        assert any("Updated region" in msg.content for msg in messages)
        
        # If there are any lint errors, they should be in the messages
        lint_warnings = [msg for msg in messages if "Warning" in msg.content]
        if lint_warnings:
            assert all("Line" in msg.content for msg in lint_warnings)


def test_patch_single_line_in_middle(temp_file):
    """Test replacing a single line in the middle of a file."""
    content = """line1
line2
line3
line4"""
    with temp_file(content) as f:
        list(patch(f, (2, 2), "new_line"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1
new_line
line3
line4"""


def test_patch_multiple_regions(temp_file):
    """Test multiple patch operations on the same file."""
    content = """line1
line2
line3
line4"""
    with temp_file(content) as f:
        # First patch
        list(patch(f, (1, 1), "new_line1"))
        # Second patch
        list(patch(f, (3, 3), "new_line3"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """new_line1
line2
new_line3
line4"""


def test_patch_empty_string(temp_file):
    """Test patching with an empty string."""
    content = """line1
line2
line3"""
    with temp_file(content) as f:
        list(patch(f, (2, 2), ""))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1

line3"""


def test_patch_multiline_with_empty_lines(temp_file):
    """Test patching with content that includes empty lines."""
    content = "line1\nline2\nline3"
    patch_content = """new_line1

new_line3"""
    with temp_file(content) as f:
        list(patch(f, (1, 3), patch_content))
        with open(f, encoding="utf-8") as f:
            assert f.read() == patch_content


def test_patch_overlapping_regions(temp_file):
    """Test patching overlapping regions in sequence."""
    content = """line1
line2
line3
line4"""
    with temp_file(content) as f:
        # First patch overlaps with second
        list(patch(f, (2, 3), "new_lines\nmore_lines"))
        list(patch(f, (3, 4), "final_lines"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1
new_lines
final_lines"""


def test_patch_remove_multiple_lines(temp_file):
    """Test removing multiple lines by patching with empty string."""
    content = """line1
line2
line3
line4
line5"""
    with temp_file(content) as f:
        # Replace lines 2-4 with empty string
        list(patch(f, (2, 4), ""))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1

line5"""

    # Test removing all lines except first and last
    with temp_file(content) as f:
        list(patch(f, (2, 4), "\n\n"))  # Explicitly preserve empty lines
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1


line5"""

    # Test removing all middle lines with no replacement
    with temp_file(content) as f:
        list(patch(f, (2, 4), ""))
        with open(f, encoding="utf-8") as f:
            assert f.read() == """line1

line5"""

def test_patch_replace_middle_to_end(temp_file):
    content = "line1\nline2\nline3\nline4\nline5\nline6"
    with temp_file(content) as f:
        list(patch(f, (3, -1), "new_line1\nnew_line2"))
        with open(f, encoding="utf-8") as f:
            assert f.read() == "line1\nline2\nnew_line1\nnew_line2"
from vibecraft.sanitizer import sanitize_command


def test_sanitize_rejects_empty_slash_command():
    result = sanitize_command("/")
    assert result.is_valid is False

    result = sanitize_command("///")
    assert result.is_valid is False


def test_sanitize_allows_basic_command():
    result = sanitize_command("/list")
    assert result.is_valid is True

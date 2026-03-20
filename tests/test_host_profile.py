from awaken.host_profile import describe_host_lines


def test_describe_host_lines_non_empty() -> None:
    lines = describe_host_lines()
    assert len(lines) >= 1
    assert lines[0]

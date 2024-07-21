from una import internal_deps

apps_in_ws = {"x"}
libs_in_ws = {"a", "b"}


def test_to_row_returns_columns_for_all_int_deps():
    expected_length = len(apps_in_ws) + len(libs_in_ws)
    collected_import_data = {"x": {"a"}, "a": {"b"}}
    flattened_imports: set[str] = set().union(*collected_import_data.values())
    rows = internal_deps.create_rows(
        apps_in_ws,
        libs_in_ws,
        collected_import_data,
        flattened_imports,  # type: ignore[reportArgumentType]
    )
    assert len(rows) == expected_length
    for columns in rows:
        assert len(columns) == expected_length

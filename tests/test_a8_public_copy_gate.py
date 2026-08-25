from tools.ai_workbook.a8_public_copy_gate import validate_public_copy


def test_customer_ready_copy_passes() -> None:
    text = "台南畢業典禮的一口點心與花藝，替成長留下明亮而溫柔的記憶。"
    assert validate_public_copy(text, forbid_dates=True) == []


def test_internal_self_talk_is_rejected() -> None:
    text = "快速導覽：公開草稿只選無人畫面，含幼兒人像素材先排除。"
    errors = validate_public_copy(text)
    assert "internal_term:快速導覽" in errors
    assert "internal_term:公開草稿" in errors
    assert "internal_term:含幼兒人像" in errors


def test_date_path_and_placeholder_are_rejected() -> None:
    text = "7 月 17 日；workbook/a8/c01.mov；[精選圖待補]"
    errors = validate_public_copy(text, forbid_dates=True)
    assert "date_exposed" in errors
    assert "local_path" in errors
    assert "file_label" in errors
    assert "placeholder" in errors

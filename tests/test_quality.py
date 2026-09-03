from pathlib import Path


def test_bad_pdf_like_output_is_rejected():
    from ts_knowledge_agent.services.quality import inspect_markdown
    report = inspect_markdown("���ƶ����˶˿��˶˿�������ЧЧ���ʸ��������UUTTSS")
    assert not report.ok
    assert "Unicode replacement" in report.errors[0]


def test_normal_markdown_is_usable():
    from ts_knowledge_agent.services.quality import inspect_markdown
    report = inspect_markdown("# Title\n\nThis is usable knowledge content with enough detail.")
    assert report.ok

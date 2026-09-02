from pathlib import Path


def test_init_uses_personal_workspace_and_shared_source_directory():
    from ts_knowledge_agent.cli.main import build_parser
    args = build_parser().parse_args(["init", "--working-directory", "D:/work", "--personal-workspace", "wanghm", "--shared-source-directory", "D:/source"])
    assert args.personal_workspace == "wanghm"
    assert str(args.shared_source_directory) == "D:/source"


def test_legacy_names_are_still_accepted():
    from ts_knowledge_agent.cli.main import build_parser
    args = build_parser().parse_args(["init", "--workdir", "D:/work", "--workspace", "wanghm", "--source-root", "D:/source"])
    assert args.personal_workspace == "wanghm"

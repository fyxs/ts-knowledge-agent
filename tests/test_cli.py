from ts_knowledge_agent.cli import main


def test_cli_without_command_prints_help(capsys):
    assert main([]) == 0
    assert "usage:" in capsys.readouterr().out

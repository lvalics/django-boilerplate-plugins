"""CLI-layer tests for install.py:main (arg handling + clean error exits)."""
import install


def test_list_exits_zero(capsys):
    assert install.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "web_security" in out  # the shipped pilot plugin is listed


def test_unknown_plugin_exits_one_without_traceback(capsys, tmp_path):
    rc = install.main(["does_not_exist", str(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "unknown plugin 'does_not_exist'" in err


def test_missing_args_exits_two():
    # argparse's parser.error() raises SystemExit(2)
    try:
        install.main([])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover
        raise AssertionError("expected SystemExit(2) for missing args")

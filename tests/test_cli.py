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


def test_files_only_flag_is_accepted(capsys, tmp_path):
    # unknown target -> clean error exit, but the flag itself must parse
    rc = install.main(["web_security", str(tmp_path), "--files-only"])
    assert rc == 1
    assert "unrecognized arguments" not in capsys.readouterr().err

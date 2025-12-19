from click.testing import CliRunner
import pytest
from unittest.mock import patch, MagicMock
from enc_server.cli import cli
import os
import json

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_admin_user():
    with patch("getpass.getuser", return_value="admin"), \
         patch.dict(os.environ, {"ENC_MODE": "SERVER"}):
        yield

@pytest.fixture
def mock_regular_user():
    with patch("getpass.getuser", return_value="user"), \
         patch.dict(os.environ, {"ENC_MODE": "SERVER"}), \
         patch("builtins.open", new_callable=MagicMock) as mock_open:
        # Mock policy file with a regular user
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({
            "users": {
                "user": {"role": "user", "permissions": ["init"]}
            }
        })
        mock_open.return_value = mock_file
        yield

@pytest.fixture
def mock_console():
    with patch("enc_server.cli.console") as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock side-effect dependencies globally."""
    with patch("enc_server.cli.get_enc_dir"):
        yield

def test_user_list_admin(runner, mock_admin_user, mock_console):
    """Test 'enc user list' as admin"""
    with patch("enc_server.cli.check_server_permission"), \
         patch("subprocess.run") as mock_run:
         
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({"users": {"admin": {"role": "admin"}}})

        result = runner.invoke(cli, ["user", "list"])
    
        assert result.exit_code == 0
        # Check that table was printed (console.print called with Table)
        assert mock_console.print.called

def test_user_list_denied_regular(runner, mock_regular_user, mock_console):
    """Test 'enc user list' as regular user -> Should Fail"""
    result = runner.invoke(cli, ["user", "list"])
    
    assert result.exit_code == 1
    # Check that error message was printed to console
    # console.print is called with a string containing "Permission Error"
    args, _ = mock_console.print.call_args
    assert "Permission Error" in str(args[0]) or "Access Denied" in str(args[0])

def test_user_remove_denied_regular(runner, mock_regular_user, mock_console):
    """Test 'enc user remove' as regular -> Should Fail"""
    result = runner.invoke(cli, ["user", "remove", "someuser"])
    assert result.exit_code == 1
    args, _ = mock_console.print.call_args
    assert "Permission Error" in str(args[0]) or "Access Denied" in str(args[0])

def test_show_users_admin(runner, mock_admin_user, mock_console):
    """Test 'enc show users' as admin -> Should call list"""
    with patch("enc_server.cli.list_users") as mock_list:
        result = runner.invoke(cli, ["show", "users"])
        assert result.exit_code == 0
        mock_list.assert_called()

def test_show_users_denied_regular(runner, mock_regular_user, mock_console):
    """Test 'enc show users' as regular -> Should Fail"""
    result = runner.invoke(cli, ["show", "users"])
    assert result.exit_code == 1
    # Since it calls list_users, it should hit the permission check and print error
    # But note: invoke might hide the permission check if it happens before invocation?
    # No, we call ctx.invoke(list_users), which runs list_users() function.
    # list_users calls ensure_admin -> console.print -> ctx.exit(1)
    
    assert mock_console.print.called
    args, _ = mock_console.print.call_args
    assert "Permission Error" in str(args[0]) or "Access Denied" in str(args[0])

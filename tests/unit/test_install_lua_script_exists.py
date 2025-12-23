import os

def test_install_lua_script_exists():
    path = os.path.join(os.getcwd(), 'scripts', 'install_lua_plugin.ps1')
    assert os.path.exists(path), 'PowerShell installer script must exist'

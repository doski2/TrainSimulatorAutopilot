import os


def test_run_e2e_scripts_exist():
    base = os.path.join(os.getcwd(), 'scripts')
    sh = os.path.join(base, 'run_e2e_tests.sh')
    ps1 = os.path.join(base, 'run_e2e_tests.ps1')
    assert os.path.exists(sh), "run_e2e_tests.sh must exist"
    assert os.path.exists(ps1), "run_e2e_tests.ps1 must exist"

import builtins
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tempfile import TemporaryDirectory

from tsc_integration import TSCIntegration

with TemporaryDirectory() as tmp:
    path = os.path.join(tmp, 'GetData.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('ControlName:CurrentSpeed\nControlValue:5.0\n')
    tsc = TSCIntegration()
    tsc.ruta_archivo = path
    calls = {'count': 0}
    orig_open = builtins.open
    def fake_open(path_arg, mode='r', *args, **kwargs):
        print('fake_open called', path_arg, mode, calls['count'])
        if os.path.abspath(path_arg) == os.path.abspath(tsc.ruta_archivo) and calls['count'] == 0:
            calls['count'] += 1
            raise PermissionError('file locked on read')
        return orig_open(path_arg, mode, *args, **kwargs)
    builtins.open = fake_open
    try:
        lines = tsc._robust_read_lines()
        print('lines read:', lines)
        print('io_metrics after read:', tsc.io_metrics)
    finally:
        builtins.open = orig_open

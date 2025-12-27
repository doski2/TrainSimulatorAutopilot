import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tsc_integration import TSCIntegration

p = r"C:\temp\GetData_test_bom_debug.txt"
content = "\ufeffControlName:SignalAspect\nControlValue:2\nControlName:KVB_SignalAspect\nControlValue:-1\n"
with open(p, 'w', encoding='utf-8') as f:
    f.write(content)
ts = TSCIntegration(ruta_archivo=p)
print('archivo existe?', ts.archivo_existe())
with open(p, 'rb') as f:
    raw = f.read()
print('raw bytes:', raw[:20])
lines = ts._robust_read_lines()
print('HAS_PORTALOCKER', getattr(__import__('tsc_integration'), 'HAS_PORTALOCKER', None))
for idx, line in enumerate(lines):
    print('line', idx, 'type', type(line), 'repr', repr(line), 'chars', [hex(ord(c)) for c in line[:4]])
parsed = ts.leer_datos_archivo()
print('parsed:', parsed)

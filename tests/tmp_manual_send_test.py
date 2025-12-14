import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tsc_integration import TSCIntegration
from pathlib import Path
import tempfile

inst = TSCIntegration()
with tempfile.TemporaryDirectory() as d:
    inst.ruta_archivo_comandos = str(Path(d)/"SendCommand.txt")
    inst.enviar_comandos({"autopilot": True})
    lua_file = Path(d)/"autopilot_commands.txt"
    print('lua_file_exists=', lua_file.exists())
    if lua_file.exists():
        print('contents:')
        print(lua_file.read_text(encoding='utf-8'))

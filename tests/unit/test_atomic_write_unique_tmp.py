import threading
from pathlib import Path

from tsc_integration import TSCIntegration


def writer(tsc, path: Path, lines):
    tsc._atomic_write_lines(str(path), lines)


def test_concurrent_atomic_writes_do_not_conflict(tmp_path):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    target = plugins / "SendCommand.txt"

    # prepare several different payloads
    payloads = [[f"val:{i}"] * 3 for i in range(8)]

    tsc = TSCIntegration()
    tsc.ruta_archivo_comandos = str(target)

    threads = []
    for p in payloads:
        t = threading.Thread(target=writer, args=(tsc, target, p))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Final file should contain exactly one of the payloads (no partial mix)
    assert target.exists()
    content = target.read_text(encoding='utf-8').strip().splitlines()
    assert any(all(line == payload[0] for line in content) for payload in payloads)

    # No leftover .tmp files in the dir
    tmp_files = list(plugins.glob('*.tmp'))
    assert tmp_files == []

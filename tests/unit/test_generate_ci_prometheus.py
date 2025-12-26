import importlib.util
from pathlib import Path


def test_generate_prometheus_ci(tmp_path):
    srcdir = tmp_path / "prometheus"
    srcdir.mkdir()
    src = srcdir / "prometheus.yml"
    dest = srcdir / "ci_prometheus.yml"

    sample = "scrape_configs:\n  - job_name: 'dashboard'\n    static_configs:\n      - targets: ['localhost:5001']\n"
    src.write_text(sample, encoding="utf-8")

    script_path = Path(".github/scripts/generate_ci_prometheus.py").resolve()
    spec = importlib.util.spec_from_file_location("generate_ci_prometheus", str(script_path))
    # Ensure spec is not None for type checkers
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    mod.generate(src, dest)

    assert dest.exists()
    content = dest.read_text(encoding="utf-8")
    assert "localhost:5001" not in content
    assert "host.docker.internal:5001" in content

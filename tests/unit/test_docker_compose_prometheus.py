import os


def test_docker_compose_contains_prometheus_service():
    # Check that docker-compose.yml has a prometheus service defined
    path = os.path.join(os.getcwd(), 'docker-compose.yml')
    assert os.path.exists(path), "docker-compose.yml must exist"
    content = open(path, encoding='utf-8').read()
    assert 'prometheus:' in content, "Expected 'prometheus' service in docker-compose.yml"
    assert 'prometheus: prom/prometheus' in content or 'image: prom/prometheus' in content

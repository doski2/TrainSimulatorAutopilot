import threading
from web_dashboard import app, request, jsonify


def test_simpleclient_post_is_thread_safe():
    # Register a simple echo route that returns the JSON body
    @app.route('/echo', methods=['POST'])
    def echo():
        data = request.get_json()
        return jsonify({'echo': data})

    results = []
    errors = []

    def worker(i):
        with app.test_client() as client:
            resp = client.post('/echo', json={'i': i})
            if resp.status_code != 200:
                errors.append((i, resp.status_code))
            else:
                results.append(resp.get_json())

    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert not errors, f"Errors during threaded requests: {errors}"
    # Ensure we have 10 results and each echoed the correct payload
    assert len(results) == 10
    received_indices = sorted([r['echo']['i'] for r in results])
    assert received_indices == list(range(10))
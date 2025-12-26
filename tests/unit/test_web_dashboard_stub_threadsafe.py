import threading

from flask import Flask, jsonify, request


def test_simpleclient_post_is_thread_safe():
    # Use a fresh Flask app so route registration is safe even if other tests
    # have already exercised the global app and triggered its first request.
    app = Flask(__name__)

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


from web_dashboard import Flask


def test_simpleclient_matches_parameterized_route_and_passes_kwargs():
    # Use import_name compatible with real Flask and stub
    app = Flask(__name__)

    @app.route('/api/control/<action>', methods=['POST'])
    def control_action(action):
        # Return the action received to assert the parameter forwarding
        return {'action': action}

    with app.test_client() as client:
        resp = client.post('/api/control/start_autopilot', json={'dummy': True})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['action'] == 'start_autopilot'

from autopilot.traction_control import TractionConfig, TractionControl


def run_stream(tc: TractionControl, samples, dt=0.1):
    for s_train, s_wheel in samples:
        if tc.detect_slip(s_train, s_wheel, dt):
            return True
    return False


def test_detect_slip_debounce():
    cfg = TractionConfig(slip_threshold=0.1, debounce_sec=0.2, ewma_alpha=0.5)
    tc = TractionControl(cfg)

    # series: below threshold then sustained above
    samples = [(20.0, 20.0)] * 2 + [(20.0, 22.5)] * 5
    assert run_stream(tc, samples, dt=0.1) is True


def test_no_false_positive_on_spike():
    cfg = TractionConfig(slip_threshold=0.1, debounce_sec=0.4, ewma_alpha=0.5)
    tc = TractionControl(cfg)

    # one short spike then normal
    samples = [(20.0, 20.0)] * 3 + [(20.0, 22.5)] * 1 + [(20.0, 20.0)] * 5
    assert run_stream(tc, samples, dt=0.1) is False


def test_recovery_threshold():
    cfg = TractionConfig(slip_threshold=0.08, recovery_threshold=0.03, debounce_sec=0.2, recovery_sec=0.2, ewma_alpha=0.6)
    tc = TractionControl(cfg)

    # trigger slip
    samples = [(10.0, 11.5)] * 4
    assert run_stream(tc, samples, dt=0.1) is True

    # then go below recovery threshold for sufficient time
    samples2 = [(10.0, 10.02)] * 4
    # continue stepping to allow recovery
    for s_train, s_wheel in samples2:
        tc.detect_slip(s_train, s_wheel, 0.1)
    # after recovery window, new slip should not trigger immediately
    assert tc.detect_slip(10.0, 11.5, 0.1) is False

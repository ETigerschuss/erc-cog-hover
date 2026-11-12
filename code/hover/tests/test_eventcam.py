"""Tests for the event-camera simulation (hover.eventcam)."""
import numpy as np

from hover import eventcam as ec


def test_register_recovers_a_known_shift():
    rng = np.random.default_rng(1)
    from scipy.ndimage import gaussian_filter
    a = gaussian_filter(rng.random((ec.N, ec.N)), 2.0)
    b = np.roll(a, (2, -3), (0, 1))                 # content at x appears at x - (3, -2)
    assert np.allclose(ec.register(a, b), [3.0, -2.0], atol=0.2)


def test_sensor_is_blind_without_movement_and_sees_with_it():
    rng = np.random.default_rng(0)
    scene = ec.make_scene(rng)
    s = ec.Sensor(rng)
    still = s.glance(scene, 0.0, 0.3)
    moved = s.glance(scene, 2.0, 0.3)
    assert still.mean() < 0.1                        # noise events only
    assert moved.mean() > 5 * still.mean()


def test_the_two_tasks_have_opposite_needs():
    r = ec.run(n_scenes=6, amps=np.array([0.0, 4.0]), verbose=False)
    assert r["target_top1"][0] == 1.0 and r["reg_ok"][0] == 0.0      # still sensor: target found, scene invisible
    assert r["reg_ok"][1] >= 0.8 and r["target_top1"][1] <= 0.5      # 4 pixels: scene registered, target mostly lost
    assert r["events_per_pixel"][1] > 10 * r["events_per_pixel"][0]


if __name__ == "__main__":
    for f in (test_register_recovers_a_known_shift, test_sensor_is_blind_without_movement_and_sees_with_it,
              test_the_two_tasks_have_opposite_needs):
        f(); print("ok", f.__name__)

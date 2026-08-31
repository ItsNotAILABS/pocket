from __future__ import annotations

import unittest


class TestGoPlane(unittest.TestCase):
    def test_go_arms_daily_and_slots(self):
        from pocket.go_plane import go, snapshot

        g = go(arm_daily=True, run_morning=False)
        self.assertTrue(g["ok"])
        self.assertEqual(g["workflow_count"], 100)
        self.assertGreaterEqual(g["active_count"], 1)
        self.assertGreaterEqual(len(g.get("armed") or []), 4)
        s = snapshot()
        self.assertIn("mw097_morning_seatbelt", s["workflows"])
        self.assertEqual(s["workflows"]["mw097_morning_seatbelt"]["status"], "armed")

    def test_power_entangles_go(self):
        from pocket.go_plane import snapshot
        from pocket.power import do, pulse

        r = do("morning health", dry=True, workflow_id="mw097_morning_seatbelt")
        self.assertTrue(r["ok"])
        slot = snapshot()["workflows"]["mw097_morning_seatbelt"]
        self.assertIn(slot["status"], ("ok", "fail", "running"))
        p = pulse()
        self.assertIsNotNone(p.get("go"))
        self.assertEqual(p["go"]["workflow_count"], 100)

    def test_mcp_go_state(self):
        from pocket.mcp_bundle import invoke

        s = invoke("pocket", "go_state")
        self.assertTrue(s.get("ok"))
        self.assertEqual(s.get("workflow_count"), 100)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest


class TestPower(unittest.TestCase):
    def test_pulse_counts(self):
        from pocket.power import pulse

        p = pulse()
        self.assertTrue(p["ok"])
        self.assertGreaterEqual(p["tools"], 200)
        self.assertEqual(p["workflows"], 100)
        self.assertGreaterEqual(p["clouds"], 8)

    def test_pick_trade(self):
        from pocket.power import pick

        p = pick("prepare a binance trade without auto spend")
        self.assertEqual(p["family"], "forge")

    def test_do_dry(self):
        from pocket.power import do

        r = do("morning health", dry=True, workflow_id="mw097_morning_seatbelt")
        self.assertTrue(r["ok"])
        self.assertEqual(r["run"]["workflow_id"], "mw097_morning_seatbelt")

    def test_vs(self):
        from pocket.power import vs_theirs

        v = vs_theirs()
        self.assertIn("/", v["score"])
        self.assertTrue(all(a["we_win"] for a in v["axes"]))

    def test_mcp(self):
        from pocket.mcp_bundle import invoke

        p = invoke("pocket", "power_pulse")
        self.assertTrue(p.get("ok"))
        self.assertEqual(p.get("workflows"), 100)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest


class TestMultiWorkflows(unittest.TestCase):
    def test_exactly_one_hundred(self):
        from pocket.multi_workflows import WORKFLOWS, catalog, families

        self.assertEqual(len(WORKFLOWS), 100)
        c = catalog()
        self.assertEqual(c["total"], 100)
        self.assertEqual(sum(families()["families"].values()), 100)
        self.assertTrue(all(w["step_count"] >= 2 for w in WORKFLOWS))

    def test_get_and_dry_run(self):
        from pocket.multi_workflows import get, run

        g = get("mw001_stack_health")
        self.assertTrue(g["ok"])
        r = run("mw001", dry=True)
        self.assertTrue(r["ok"])
        self.assertGreaterEqual(r["total"], 2)
        self.assertTrue(r["dry"])

    def test_live_lightweight(self):
        from pocket.multi_workflows import run

        r = run("mw009_decide_goal", params={"goal": "trade BTC"})
        self.assertTrue(r.get("ok"), r)
        self.assertGreaterEqual(r["passed"], 2)

    def test_mcp_invoke(self):
        from pocket.mcp_bundle import invoke

        c = invoke("pocket", "multi_workflows")
        self.assertEqual(c.get("total"), 100)
        g = invoke("pocket", "multi_workflow_get", name="mw060_billing_table")
        self.assertTrue(g.get("ok"))


if __name__ == "__main__":
    unittest.main()

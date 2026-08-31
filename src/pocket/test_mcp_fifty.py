from __future__ import annotations

import unittest


class TestMcpFifty(unittest.TestCase):
    def test_exactly_two_hundred(self):
        from pocket.mcp_fifty import catalog, ids, universal_ids

        c = catalog()
        self.assertEqual(c["count"], 200)
        self.assertEqual(len(ids()), 200)
        self.assertEqual(c["universal"], 60)
        self.assertEqual(len(universal_ids()), 60)

    def test_ping_and_ports(self):
        from pocket.mcp_fifty import run

        self.assertTrue(run("universal_ping")["ok"])
        self.assertTrue(run("pocket_universal_ping")["ok"])
        ports = run("universal_ports")
        self.assertEqual(ports["ports"]["pocket"], 8787)
        self.assertEqual(ports["ports"]["forge"], 8789)
        self.assertNotEqual(ports["ports"]["forge"], 8788)

    def test_invoke_router(self):
        from pocket.mcp_bundle import invoke

        r = invoke("universal", "universal_whoami")
        self.assertTrue(r.get("ok"))
        self.assertEqual(r.get("product"), "POCKET")

        r2 = invoke("pocket", "universal_catalog")
        self.assertEqual(r2.get("count"), 200)

    def test_extras_ok(self):
        from pocket.mcp_fifty import run

        self.assertTrue(run("universal_uuid")["ok"])
        self.assertTrue(run("forge_port")["ok"])
        self.assertTrue(run("billing_pro")["ok"])
        self.assertEqual(run("billing_pro")["id"], "pocket_pro")

    def test_billing_alias(self):
        from pocket.mcp_fifty import run

        g = run("billing_lookup", {"name": "monthly_pro"})
        self.assertTrue(g.get("ok"))
        self.assertEqual(g["plan"]["id"], "pocket_pro")


if __name__ == "__main__":
    unittest.main()

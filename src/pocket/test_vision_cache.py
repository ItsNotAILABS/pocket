from __future__ import annotations

import time
import unittest
from pathlib import Path
from unittest import mock


class TestVisionCacheNeverWalks(unittest.TestCase):
    def test_observe_force_false_no_walk(self):
        from pocket import vision_core

        with mock.patch.object(vision_core, "LAST_OBS", Path("__missing_obs__.json")):
            with mock.patch.object(vision_core, "emit") as emit:
                out = vision_core.observe(force=False)
        self.assertFalse(out.get("ok"))
        self.assertIn("no observation yet", out.get("error") or "")
        emit.assert_not_called()

    def test_page_force_false_no_walk(self):
        from pocket import page_renderer

        missing = Path("__missing_page__.json")
        with mock.patch.object(page_renderer, "PAGE_PATH", missing):
            out = page_renderer.render_full_page(force=False)
        self.assertFalse(out.get("ok"))
        self.assertIn("no page yet", out.get("error") or "")

    def test_observe_returns_stale_cache(self):
        from pocket import vision_core

        class _P:
            def is_file(self):
                return True

            def read_text(self, encoding="utf-8"):
                return '{"ok": true, "at": 1, "brief": "desk"}'

            def stat(self):
                class S:
                    st_mtime = time.time() - 99

                return S()

        with mock.patch.object(vision_core, "LAST_OBS", _P()):
            with mock.patch.object(vision_core, "emit") as emit:
                out = vision_core.observe(force=False)
        self.assertTrue(out.get("cached"))
        self.assertEqual(out.get("brief"), "desk")
        emit.assert_not_called()


if __name__ == "__main__":
    unittest.main()

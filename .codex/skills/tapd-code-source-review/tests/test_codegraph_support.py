from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.codegraph_support import read_codex_mcp_registration


class ReadCodexMcpRegistrationTests(unittest.TestCase):
    def test_reads_valid_codegraph_registration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            config_path.write_text(
                '[mcp_servers.codegraph]\ncommand = "codegraph"\nargs = ["serve", "--mcp"]\nenabled = true\n',
                encoding="utf-8",
            )

            command, args, enabled = read_codex_mcp_registration(config_path)

            self.assertEqual(command, "codegraph")
            self.assertEqual(args, ("serve", "--mcp"))
            self.assertTrue(enabled)

    def test_reports_missing_registration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            config_path.write_text('[mcp_servers.other]\ncommand = "other"\n', encoding="utf-8")

            command, args, enabled = read_codex_mcp_registration(config_path)

            self.assertEqual(command, "")
            self.assertEqual(args, ())
            self.assertFalse(enabled)


if __name__ == "__main__":
    unittest.main()

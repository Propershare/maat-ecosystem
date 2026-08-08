#!/usr/bin/env python3
"""T3 credential split — unit tests (no real secrets)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from maat_memory.maat_credentials import (  # noqa: E402
    BROKER_KEYS,
    CredentialError,
    KeyClass,
    assert_agent_cannot_see,
    classify_key,
    load_agent_env,
    load_broker_env,
    require_role,
    split_dotenv,
    split_env_map,
)


class TestCredentialsT3(unittest.TestCase):
    def test_01_openrouter_is_broker(self):
        self.assertEqual(classify_key("OPENROUTER_API_KEY"), KeyClass.BROKER)

    def test_02_discord_token_broker(self):
        self.assertEqual(classify_key("DISCORD_BOT_TOKEN"), KeyClass.BROKER)

    def test_03_memory_url_agent(self):
        self.assertEqual(classify_key("MAAT_MEMORY_URL"), KeyClass.AGENT)

    def test_04_pgvector_is_broker(self):
        self.assertEqual(classify_key("PGVECTOR_DB_URL"), KeyClass.BROKER)

    def test_05_unknown_secretish_broker(self):
        self.assertEqual(classify_key("WEIRD_VENDOR_API_KEY"), KeyClass.BROKER)

    def test_06_split_separates(self):
        agent, broker, debt = split_env_map(
            {
                "OPENROUTER_API_KEY": "sk-test",
                "MAAT_MEMORY_URL": "http://127.0.0.1:8022",
                "PGVECTOR_DB_URL": "postgres://x",
            }
        )
        self.assertIn("OPENROUTER_API_KEY", broker)
        self.assertNotIn("OPENROUTER_API_KEY", agent)
        self.assertIn("MAAT_MEMORY_URL", agent)
        self.assertIn("PGVECTOR_DB_URL", broker)
        self.assertNotIn("PGVECTOR_DB_URL", agent)

    def test_07_split_writes_files(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / ".env"
            src.write_text(
                "OPENROUTER_API_KEY=sk-live-fake\n"
                "MAAT_MEMORY_URL=http://127.0.0.1:8022\n"
                "DISCORD_BOT_TOKEN=discord-fake\n"
                "WHATSAPP_ENABLED=true\n",
                encoding="utf-8",
            )
            result = split_dotenv(src)
            self.assertTrue(result.broker_path.exists())
            self.assertTrue(result.agent_path.exists())
            agent_txt = result.agent_path.read_text()
            broker_txt = result.broker_path.read_text()
            self.assertNotIn("OPENROUTER_API_KEY", agent_txt)
            self.assertNotIn("DISCORD_BOT_TOKEN", agent_txt)
            self.assertIn("OPENROUTER_API_KEY", broker_txt)
            self.assertIn("MAAT_MEMORY_URL", agent_txt)
            # rewritten source must not contain broker values
            src_txt = src.read_text()
            self.assertNotIn("sk-live-fake", src_txt)
            self.assertNotIn("discord-fake", src_txt)

    def test_08_agent_load_refuses_broker_key_in_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / ".env.agent"
            p.write_text("OPENROUTER_API_KEY=should-not\n", encoding="utf-8")
            with self.assertRaises(CredentialError):
                load_agent_env([p], into_environ=False)

    def test_09_agent_load_ok(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / ".env.agent"
            p.write_text("MAAT_MEMORY_URL=http://x\n", encoding="utf-8")
            got = load_agent_env([p], into_environ=False)
            self.assertEqual(got["MAAT_MEMORY_URL"], "http://x")

    def test_10_broker_requires_role(self):
        old = os.environ.pop("MAAT_CREDENTIAL_ROLE", None)
        try:
            with self.assertRaises(CredentialError):
                require_role("broker")
        finally:
            if old is not None:
                os.environ["MAAT_CREDENTIAL_ROLE"] = old

    def test_11_broker_load_with_role(self):
        with tempfile.TemporaryDirectory() as td:
            agent = Path(td) / ".env.agent"
            broker = Path(td) / ".env.broker"
            agent.write_text("MAAT_MEMORY_URL=http://x\n", encoding="utf-8")
            broker.write_text("OPENROUTER_API_KEY=sk-b\n", encoding="utf-8")
            os.environ["MAAT_CREDENTIAL_ROLE"] = "broker"
            try:
                # load_broker_env also_agent=True would call load_agent_env which
                # refuses if role is broker — so also_agent=False for unit path
                got = load_broker_env([broker], into_environ=False, also_agent=False)
                self.assertEqual(got["OPENROUTER_API_KEY"], "sk-b")
            finally:
                os.environ.pop("MAAT_CREDENTIAL_ROLE", None)

    def test_12_absence_not_broker(self):
        old = os.environ.pop("MAAT_CREDENTIAL_ROLE", None)
        try:
            with self.assertRaises(CredentialError) as cm:
                require_role("broker")
            self.assertIn("absence", str(cm.exception).lower())
        finally:
            if old is not None:
                os.environ["MAAT_CREDENTIAL_ROLE"] = old

    def test_13_assert_agent_cannot_see(self):
        with self.assertRaises(CredentialError):
            assert_agent_cannot_see(["OPENROUTER_API_KEY"], {"OPENROUTER_API_KEY": "x"})
        assert_agent_cannot_see(["OPENROUTER_API_KEY"], {"MAAT_MEMORY_URL": "http://x"})

    def test_14_broker_keys_nonempty(self):
        self.assertIn("OPENROUTER_API_KEY", BROKER_KEYS)
        self.assertIn("HERMES_GATEWAY_TOKEN", BROKER_KEYS)

    def test_15_gateway_token_not_agent(self):
        self.assertEqual(classify_key("HERMES_GATEWAY_TOKEN"), KeyClass.BROKER)

    def test_16_ka_api_key_broker(self):
        self.assertEqual(classify_key("KA_API_KEY"), KeyClass.BROKER)

    def test_17_rewrite_preserves_agent_flags(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / ".env"
            src.write_text("WHATSAPP_ENABLED=false\nOPENROUTER_API_KEY=sk-z\n", encoding="utf-8")
            split_dotenv(src)
            self.assertIn("WHATSAPP_ENABLED=false", src.read_text())

    def test_18_chmod_600(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / ".env"
            src.write_text("OPENROUTER_API_KEY=sk\nMAAT_MEMORY_URL=http://x\n", encoding="utf-8")
            r = split_dotenv(src)
            self.assertEqual(oct(r.agent_path.stat().st_mode & 0o777), "0o600")
            self.assertEqual(oct(r.broker_path.stat().st_mode & 0o777), "0o600")

    def test_19_pgvector_in_broker_result(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / ".env"
            src.write_text("PGVECTOR_DB_URL=postgres://x\nOPENROUTER_API_KEY=sk\n", encoding="utf-8")
            r = split_dotenv(src)
            self.assertIn("PGVECTOR_DB_URL", r.broker_keys)
            self.assertIn("OPENROUTER_API_KEY", r.broker_keys)
            self.assertNotIn("PGVECTOR_DB_URL", r.agent_keys)

    def test_20_agent_environ_no_openrouter_after_split_load(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / ".env"
            src.write_text(
                "OPENROUTER_API_KEY=sk-should-vanish\nMAAT_MEMORY_URL=http://127.0.0.1:9\n",
                encoding="utf-8",
            )
            r = split_dotenv(src)
            os.environ.pop("OPENROUTER_API_KEY", None)
            loaded = load_agent_env([r.agent_path], into_environ=False)
            self.assertNotIn("OPENROUTER_API_KEY", loaded)
            assert_agent_cannot_see(["OPENROUTER_API_KEY"], loaded)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCredentialsT3)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ran = result.testsRun
    failed = len(result.failures) + len(result.errors)
    print(f"\n{ran - failed}/{ran} controls held")
    raise SystemExit(0 if result.wasSuccessful() and ran == 20 else 1)

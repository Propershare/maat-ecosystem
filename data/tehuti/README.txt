Canonical Tehuti / UKMT / RBG layout under the lab root (~/.n8n/data/tehuti/).

ukmt-rbg-dataset/
  UKMT + RBG text corpus (canon-UKMT/, rbg_library/*.txt), MAAT_Blueprint_Playbook.md,
  ka2_agent_config.json, ka2_agent_system_prompt.md.
  Source: Tehuti-Dataset snapshot from USB (2026-04-13 zip).

pdf-library/
  Large PDF library (~5.5 GB) extracted from maatlangchain/docs/Tehutidata.db.rar.
  Letter subfolders (A/, U/, T-3/, …) plus PDFs at top level.

archives/
  Tehuti-Dataset_2026-04-13_175309.zip — provenance copy of the UKMT/RBG snapshot.

Original packed archive (not duplicated here): maatlangchain/docs/Tehutidata.db.rar

Ingestion / RAG: point chunkers at ukmt-rbg-dataset/ and/or pdf-library/ as needed.

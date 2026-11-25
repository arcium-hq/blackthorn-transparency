#!/usr/bin/env python3
"""Add one release to the log: policies/<digest>/policy.txt and statement.json.
Pushing them to main signs the statement (.github/workflows/sign.yml).

Usage: add-release.py POLICY_TEXT ROSTER_JSON --host H [--host H...] --model DIGEST [--model ...]
                      --source-revision REV [--released YYYY-MM-DD]
POLICY_TEXT is the text the host serves at /v1/attestation/policy (and the
parties enforce); ROSTER_JSON the parties' identities.json."""
import argparse
import datetime
import hashlib
import json
import os
import sys

POLICY_DOMAIN = b"bllm gateway policy v1\0"

parser = argparse.ArgumentParser()
parser.add_argument("policy")
parser.add_argument("roster")
parser.add_argument("--host", action="append", required=True)
parser.add_argument("--model", action="append", required=True)
parser.add_argument("--source-revision", required=True)
parser.add_argument("--released", default=datetime.date.today().isoformat())
args = parser.parse_args()

text = open(args.policy, "rb").read()
digest = hashlib.sha256(POLICY_DOMAIN + text).hexdigest()
parties = json.load(open(args.roster))["parties"]
for key in parties + args.model:
    bytes.fromhex(key)
    assert len(key) == 64, key
statement = {
    "format": "blackthorn-release/1",
    "policy_sha256": digest,
    "parties": parties,
    "hosts": sorted(args.host),
    "models": args.model,
    "source_revision": args.source_revision,
    "released": args.released,
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "policies", digest)
if os.path.exists(os.path.join(out, "statement.json")):
    sys.exit(f"policies/{digest} is in the log already")
os.makedirs(out)
open(os.path.join(out, "policy.txt"), "wb").write(text)
with open(os.path.join(out, "statement.json"), "w") as f:
    json.dump(statement, f, indent=2)
    f.write("\n")
print(f"policies/{digest}")

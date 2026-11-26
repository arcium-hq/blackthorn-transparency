# Blackthorn transparency log

Every release of Blackthorn's hosted API, as the MPC parties run it: the gateway policy they enforce and their public keys. Each release is signed into [Sigstore](https://www.sigstore.dev)'s public transparency log, [Rekor](https://search.sigstore.dev), by this repository's own workflow. Nobody can remove or rewrite an entry, including Arcium.

The Blackthorn client checks the log. Each time it attests a GPU session, the parties sign the digest of the policy they enforce. `blackthorn verify`, `blackthorn status` and the web chat's Security panel then check that:

1. the policy is logged here, in a statement signed by this repository's workflow into Rekor;
2. the statement names the parties whose signatures the client checked;
3. when a session is open, the statement lists the model that session's keys are bound to.

If any of these fails, so does the check. A policy the hosted API runs without logging it, or a party key swapped quietly, shows up as a failed check instead of going unnoticed.

## What's here

```
policies/<policy sha256>/
  policy.txt              the policy text, as the host serves it at /v1/attestation/policy
  statement.json          the release: policy digest, party keys, hosts, models
  statement.sigstore.json the Sigstore bundle: certificate, signature, Rekor entry
```

## Models

A statement names each model by its weights digest: blackthorn-verify's SHA-256 tree over the exported FP8 weights, which the engine computes on the GPU when it starts. Statements from 2026-11-26 on also carry the names (`model_names`). The digests so far:

| Weights digest | Model |
| --- | --- |
| `34a1dde68b39bba474caceb334bedb57f2a6fdc8aff61e83096ca06622d12262` | Qwen 3.8 27B Abliterated, FP8 (`qwen3.8-27b-bllm`) |
| `2844a322ec7b9d7811fc061b70b928dceb21d02d77151a4dfab96bdf65eed1cd` | Qwen 3.8 27B, FP8 |

`<policy sha256>` is the digest the parties sign: SHA-256 over `bllm gateway policy v1`, a zero byte, then `policy.txt`.

```sh
(printf 'bllm gateway policy v1\0'; cat policy.txt) | sha256sum
```

The log starts with the release of 2026-11-24. Earlier policies are not in it.

## Check an entry yourself

With [cosign](https://docs.sigstore.dev/cosign/system_config/installation/):

```sh
cd policies/<policy sha256>
cosign verify-blob statement.json --bundle statement.sigstore.json \
  --certificate-identity https://github.com/arcium-hq/blackthorn-transparency/.github/workflows/sign.yml@refs/heads/main \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

To see every release ever signed, search Rekor for that identity, for example with [rekor-monitor](https://github.com/sigstore/rekor-monitor). A release signed into Rekor but missing here is as visible there as one listed here.

## What it shows, and what it doesn't

It shows that every policy and set of party keys the client accepts was published, permanently, by this repository's workflow. It doesn't show that a policy is a good one: that is for you, and anyone else, to read. Nor does it show how the parties are run: that is in the trust model of Blackthorn's docs.

## Adding a release

```sh
./add-release.py POLICY_TEXT identities.json --host bt-api.arcium.com --model '<weights digest>=<name>' --source-revision <rev>
git add policies && git commit && git push
```

The push runs [`sign.yml`](.github/workflows/sign.yml), which signs the new statement and commits its bundle. A release goes into the log before the hosted API serves it.

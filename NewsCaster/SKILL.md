---
name: newscaster-daily-digest
description: 前日(JST 00:00-23:59)公開のナルエビちゃんニュース(news.nullevi.app)を Gmail で日次ダイジェスト配信するスキル。description を再要約せず、整形して送信する。
---

# NewsCaster

ナルエビちゃんニュース RSS の前日分を Gmail で配信する Python スキルです。ローカル実行と Codex Cloud 実行の両方に対応します。

## Target

- Feed: `https://news.nullevi.app/rss`
- Date range: JST 前日 00:00:00-23:59:59.999999
- Output: plain text email
- Summary policy: RSS `description` を再要約せず、そのまま整形する

## Commands

```bash
python scripts/main.py validate-config
python scripts/main.py dry-run
python scripts/main.py test
python scripts/main.py run
python -m pytest scripts/tests/ -q
```

## Codex Cloud

Codex Cloud environment setup:

```bash
cd NewsCaster
bash scripts/codex_cloud_setup.sh
```

Required environment:

- `NEWSCASTER_SENDER_EMAIL`
- `NEWSCASTER_RECIPIENT_EMAIL`
- `NEWSCASTER_OAUTH_TOKEN_JSON` or `NEWSCASTER_OAUTH_TOKEN_PATH`

Prefer configuring `NEWSCASTER_OAUTH_TOKEN_JSON` as a Codex Cloud secret. The setup script materializes it to `$HOME/.newscaster/oauth_token.json` because Codex Cloud secrets are setup-only and are not available in the agent phase.

Enable Codex Cloud agent internet access when running `dry-run`, `test`, or `run`; those commands need RSS and Gmail API access.

## Results

| Result | Meaning |
|---|---|
| `SENT` | digest sent and state updated |
| `NO_ITEMS` | no entries for the target date; no email |
| `ALREADY_SENT` | target date already sent; no email |
| `DRY_RUN` | formatted output only; no send/state update |

## Environment variables

| Var | Required | Default |
|---|---:|---|
| `NEWSCASTER_SENDER_EMAIL` | yes | - |
| `NEWSCASTER_RECIPIENT_EMAIL` | yes | - |
| `NEWSCASTER_OAUTH_TOKEN_PATH` | yes* | - |
| `NEWSCASTER_OAUTH_TOKEN_JSON` | yes* | - |
| `NEWSCASTER_RSS_URL` | no | `https://news.nullevi.app/rss` |
| `NEWSCASTER_USER_AGENT` | no | Chrome-like UA |
| `NEWSCASTER_STATE_DIR` | no | repo `state/`, or `$HOME/.newscaster/state` via Cloud setup |
| `NEWSCASTER_MAIL_RETRY_COUNT` | no | `3` |

\* Either token path or token JSON is required.

## Failure modes

- exit `1`: RSS fetch or Gmail send failed
- exit `2`: missing/invalid configuration
- exit `3`: OAuth/Gmail authentication failed

`run` uses `JsonStateStore` to prevent duplicate sends for the same target date. Codex Cloud container state is not long-term durable storage, so move state to an external store if strict long-term idempotency is required.

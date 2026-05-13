# Codex Cloud Setup

NewsCaster can run in Codex Cloud, but it needs an explicit environment setup because it sends mail through Gmail and fetches an external RSS feed.

## Codex Automation

Codex Automations には [`automation.toml`](automation.toml) を登録用メモとして使ってください。

- Name: `ナルエビちゃんニュース日次配信`
- Timezone: `Asia/Tokyo`
- Schedule: `FREQ=DAILY;BYHOUR=0;BYMINUTE=10;BYSECOND=0`（毎日 00:10 JST）
- Working directory: `NewsCaster`
- Prompt: `automation.toml` の `prompt`

Automation 実行前に、下記の Codex Cloud Environment setup を完了してください。

## Environment setup

In Codex Cloud environment settings, use:

```bash
cd NewsCaster
bash scripts/codex_cloud_setup.sh
```

Set these environment variables:

| Variable | Kind | Notes |
|---|---|---|
| `NEWSCASTER_SENDER_EMAIL` | env var | Gmail sender address |
| `NEWSCASTER_RECIPIENT_EMAIL` | env var | Digest recipient address |
| `NEWSCASTER_OAUTH_TOKEN_JSON` | secret recommended | OAuth token JSON with Gmail send scope |
| `NEWSCASTER_RSS_URL` | optional env var | Defaults to `https://news.nullevi.app/rss` |
| `NEWSCASTER_MAIL_RETRY_COUNT` | optional env var | Defaults to `3` |

Codex Cloud secrets are only available to setup scripts. The setup script materializes `NEWSCASTER_OAUTH_TOKEN_JSON` to `$HOME/.newscaster/oauth_token.json` and persists `NEWSCASTER_OAUTH_TOKEN_PATH` for the agent phase. Seeing `NEWSCASTER_OAUTH_TOKEN_JSON` listed under **Secrets** in the environment settings is correct; it is not expected to appear when an agent runs `env` later. If the secret was added or changed while setup caching is enabled, reset the setup cache so `scripts/codex_cloud_setup.sh` runs again and can materialize the secret.

## Internet access

Dependency installation runs during setup. Actual NewsCaster execution also needs network access:

- RSS: `https://news.nullevi.app/rss`
- Gmail OAuth/API: `https://oauth2.googleapis.com` and Gmail API endpoints

Enable agent internet access for tasks that run:

```bash
python scripts/main.py dry-run
python scripts/main.py test
python scripts/main.py run
```

## Validation commands

```bash
cd NewsCaster
python -m pytest scripts/tests/ -q
python scripts/main.py validate-config
python scripts/main.py dry-run
```

`dry-run` fetches RSS and formats the digest but does not send email. `run` sends the email every time it is executed for a target date with items.

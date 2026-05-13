# Codex Cloud Setup

NewsCaster can run in Codex Cloud, but it needs an explicit environment setup because it sends mail through Gmail and fetches an external RSS feed.

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

Codex Cloud secrets are only available to setup scripts. The setup script materializes `NEWSCASTER_OAUTH_TOKEN_JSON` to `$HOME/.newscaster/oauth_token.json` and persists `NEWSCASTER_OAUTH_TOKEN_PATH` for the agent phase.

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

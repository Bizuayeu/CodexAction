# NewsCaster Agent Notes

NewsCaster lives in the `NewsCaster/` subdirectory of the repo. Run all project commands from this directory unless a task says otherwise.

## Codex Cloud setup

Use this setup script in the Codex Cloud environment:

```bash
cd NewsCaster
bash scripts/codex_cloud_setup.sh
```

Required environment variables:

- `NEWSCASTER_SENDER_EMAIL`
- `NEWSCASTER_RECIPIENT_EMAIL`
- Either `NEWSCASTER_OAUTH_TOKEN_JSON` or `NEWSCASTER_OAUTH_TOKEN_PATH`

For Codex Cloud, prefer putting the OAuth token JSON in a secret named `NEWSCASTER_OAUTH_TOKEN_JSON`. Secrets are available only during the setup phase, so `scripts/codex_cloud_setup.sh` writes the token to `$HOME/.newscaster/oauth_token.json` and persists `NEWSCASTER_OAUTH_TOKEN_PATH` through `$HOME/.bashrc`. If a task sees the secret in the Codex Cloud settings UI but not in `env`, treat that as expected; if the materialized token file is missing, reset the setup cache and rerun setup.

Actual `run`, `dry-run`, and `test` commands need outbound network access for the RSS feed and Gmail API. Enable Codex Cloud agent internet access for tasks that execute those commands.

## Checks

```bash
python -m pytest scripts/tests/ -q
python scripts/main.py validate-config
python scripts/main.py dry-run
```

`validate-config`, `test`, and `run` require the NewsCaster environment variables above. `dry-run` fetches and formats RSS without mail delivery settings, but still needs outbound access to the RSS feed. Do not commit token files, `.env`, virtualenvs, coverage output, or cache directories.

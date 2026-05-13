# NewsCaster

🦐 [ナルエビちゃんニュース](https://news.nullevi.app) の前日エントリを Gmail で配信する Python スキルです。ローカル実行と Codex Cloud 実行の両方を想定しています。

## Local Quickstart

```powershell
cd C:\Users\anyth\DEV\sandbox\Codex\NewsCaster

python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

$env:NEWSCASTER_SENDER_EMAIL = "<your-sender>@gmail.com"
$env:NEWSCASTER_RECIPIENT_EMAIL = "<your-recipient>@gmail.com"
$env:NEWSCASTER_OAUTH_TOKEN_PATH = "C:\path\to\token.json"

python scripts/main.py validate-config
python scripts/main.py dry-run
python scripts/main.py test
python scripts/main.py run
```

## Codex Cloud

Codex Cloud では setup phase と agent phase で secret の扱いが違うため、専用 setup script を使います。

```bash
cd NewsCaster
bash scripts/codex_cloud_setup.sh
```

Codex Cloud Environment には以下を設定してください。

| Var | Kind | Required | Notes |
|---|---|---:|---|
| `NEWSCASTER_SENDER_EMAIL` | env var | yes | 送信元 Gmail アドレス |
| `NEWSCASTER_RECIPIENT_EMAIL` | env var | yes | 配信先 Gmail アドレス |
| `NEWSCASTER_OAUTH_TOKEN_JSON` | secret recommended | yes* | Gmail send scope を含む OAuth token JSON |
| `NEWSCASTER_OAUTH_TOKEN_PATH` | env var | yes* | token file を直接使う場合 |
| `NEWSCASTER_RSS_URL` | env var | no | 既定: `https://news.nullevi.app/rss` |
| `NEWSCASTER_MAIL_RETRY_COUNT` | env var | no | 既定: `3` |

\* `NEWSCASTER_OAUTH_TOKEN_JSON` または `NEWSCASTER_OAUTH_TOKEN_PATH` のどちらかが必要です。Codex Cloud secret は setup script のみで利用できるため、`NEWSCASTER_OAUTH_TOKEN_JSON` を secret にした場合は `scripts/codex_cloud_setup.sh` が `$HOME/.newscaster/oauth_token.json` に materialize し、agent phase 用に `NEWSCASTER_OAUTH_TOKEN_PATH` を永続化します。環境設定画面の **シークレット** に `NEWSCASTER_OAUTH_TOKEN_JSON` が表示されていれば登録はされていますが、agent phase の `env` には直接表示されません。secret の追加・変更後に setup cache が有効な場合は、キャッシュをリセットして setup script を再実行してください。

実行時は RSS と Gmail API へアクセスするため、`dry-run` / `test` / `run` を Cloud task で実行する場合は Codex Cloud の agent internet access を有効にしてください。詳細は [CLOUD.md](CLOUD.md) を参照。

## Commands

```bash
python scripts/main.py validate-config
python scripts/main.py dry-run
python scripts/main.py test
python scripts/main.py run
python -m pytest scripts/tests/ -q
```

| Command | Behavior | Exit code |
|---|---|---|
| `validate-config` | 必須 env vars を検証 | `0` OK, `2` config error |
| `dry-run` | RSS 取得、前日分抽出、本文整形。送信はしない。メール送信設定は不要 | `0` OK |
| `test` | Gmail へテストメールを 1 通送信 | `0` OK, `3` auth error |
| `run` | RSS 取得、整形、送信 | `0` OK, `1` fetch/mail error, `2` config error, `3` auth error |

## Repeat Runs

NewsCaster は送信状態を保存しません。`run` を同じ対象日に複数回実行すると、その回数だけメールを送信します。本文確認だけをしたい場合は `dry-run` を使ってください。

## Troubleshooting

### `Configuration errors: NEWSCASTER_OAUTH_TOKEN_PATH or NEWSCASTER_OAUTH_TOKEN_JSON is required`

OAuth token を env var か file path で設定してください。Codex Cloud では `NEWSCASTER_OAUTH_TOKEN_JSON` を secret にする構成を推奨します。

### RSS が 403 Forbidden

`NEWSCASTER_USER_AGENT` が Bot 系 UA になっていないか確認してください。既定では Chrome 系 UA を使います。

### Gmail API `403 PERMISSION_DENIED`

token JSON の scope に `https://www.googleapis.com/auth/gmail.send` が含まれているか確認してください。

### `CERTIFICATE_VERIFY_FAILED`

`httplib2` が独自 CA store を使うため、Linux 環境では `HTTPLIB2_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` が必要になる場合があります。`scripts/codex_cloud_setup.sh` と `scripts/bootstrap.sh` は利用可能な CA bundle を自動設定します。

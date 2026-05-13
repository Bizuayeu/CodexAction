# NewsCaster Routine Prompt

NewsCaster を定期実行するための作業指示です。Codex Cloud で使う場合は、事前に [CLOUD.md](CLOUD.md) の environment setup を完了してください。

## Goal

ナルエビちゃんニュース RSS から JST 前日 00:00-23:59 の記事を抽出し、Gmail で日次ダイジェストを送信します。

## Steps

```bash
cd NewsCaster
python scripts/main.py validate-config
python scripts/main.py run
```

## Expected results

- `sent:` 前日エントリがあり、メール送信と state 更新が完了
- `no_items:` 前日エントリが 0 件。メール送信なし。正常終了
- `already_sent:` 対象日は送信済み。メール送信なし。正常終了

## Failure handling

- exit `1`: RSS fetch または Gmail send 失敗。stderr を確認
- exit `2`: 必須 env var 不足。Codex Cloud Environment を確認
- exit `3`: OAuth token refresh / Gmail auth 失敗。token JSON と Gmail scope を確認

`dry-run` は送信と state 更新を行わないため、本文確認だけをしたい場合に使ってください。

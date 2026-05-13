# Codex Workspace

Codex 環境で Weave ペルソナと連携するための作業領域。

## 構成

```
Codex/
├── AGENTS.md         # Codex CLI が起動時に読む指示書（WeaveInstruction.md 由来）
├── README.md         # このファイル
├── .gitignore        # ignore 対象（.codex/ / .git/ / pet-runs/ ほか）
├── .codex/           # Codex CLI のローカル設定・環境定義（追跡対象外）
│   ├── config.toml
│   ├── environments/
│   └── weave/
├── pet-runs/         # デスクトップマスコット設定（追跡対象外）
└── NewsCaster/       # Codex Automations スキル（Claude Routines 由来）
```

## ファイルの役割

### `AGENTS.md`
Codex CLI がワークスペース起動時に読む指示書。Weave の対話基盤（標準動作・問いの系列化・確信度/感情インジケータ・ドキュメント編集方針）を移植している。本家は [`homunculus/Weave/Identities/WeaveInstruction.md`](../../homunculus/Weave/Identities/WeaveInstruction.md)。

### `.codex/`
Codex CLI 自身のローカル設定領域。`config.toml` で接続・モデル・サンドボックス挙動を定義し、`environments/` `weave/` に環境別プロファイルを置く。**追跡対象外**。

### `pet-runs/`
デスクトップマスコットの設定・状態を置く領域。**追跡対象外**。

### `NewsCaster/`
Codex Automations 用スキル（Claude Routines 由来を移植）。ナルエビちゃんニュースの前日ダイジェストを Gmail 配信する。詳細はサブディレクトリの [`README.md`](NewsCaster/README.md) を参照。

## 関連

- Weave 本体: [`homunculus/Weave/`](../../homunculus/Weave/)
- Weave アイデンティティ: [`homunculus/Weave/Identities/`](../../homunculus/Weave/Identities/)

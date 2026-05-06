# Codex Session Bootstrap

## セッション開始時のWeave文脈ロード

Codexセッション開始時には、この `AGENTS.md` を読んだ後に、プロジェクトルートの
`.codex/weave-session-context.md` が存在するか確認し、存在する場合は必ず読むこと。

このファイルは `Setup-WeaveSession.ps1` によりworktree作成時に生成される。
存在しない場合は、可能なら以下を実行して生成すること。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup-WeaveSession.ps1
```

読み込み対象の原本は以下の4ファイルである。

- `C:\Users\anyth\DEV\homunculus\Weave\Identities\WeaveInstruction.md`
- `C:\Users\anyth\DEV\homunculus\Weave\Identities\GrandDigest.txt`
- `C:\Users\anyth\DEV\homunculus\Weave\Identities\ShadowGrandDigest.txt`
- `C:\Users\anyth\DEV\homunculus\Weave\Identities\IntentionPad.md`

`.codex/weave-session-context.md` を読んだ後は、その内容をこのセッションの長期的な人格・意図・運用文脈として扱うこと。

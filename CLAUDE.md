# CLAUDE.md

請到 docs/AGENTS.md 查看開發規範。

## tools for claude code

- 你可以使用 gemini cli 來呼叫 gemini cli 這個工具做事情， gemini cli 的上下文 token 很大，請你用它找專案裡的程式碼，上網查資料等。但禁止使用它修改或刪除檔案。這是一個使用範例 `Bash(gemini -p "找出專案裡使用 xAI 的地方")`
- 你可以多開 gemini cli session 來平行運作，以免等待回應太久而耽誤了工作。

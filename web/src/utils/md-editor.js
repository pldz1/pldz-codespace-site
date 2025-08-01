import { config } from "md-editor-v3";
import { lineNumbers } from "@codemirror/view";

import "md-editor-v3/lib/preview.css";

// 配置编辑界面显示行号和字数
config({
  codeMirrorExtensions(_theme, extensions) {
    return [...extensions, lineNumbers()];
  },
});

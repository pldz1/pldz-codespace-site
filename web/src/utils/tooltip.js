import tippy from "tippy.js";

class ToolTip {
  constructor() {
    //
  }

  /**
   * 加载文章页的工具提示
   */
  static loadArticleTooltip() {
    tippy("#to-top", {
      content: "回到顶部",
      placement: "left",
      theme: "light-border",
      arrow: true,
    });

    tippy("#to-bottom", {
      content: "回到底部",
      placement: "left",
      theme: "light-border",
      arrow: true,
    });

    tippy("#to-csdn", {
      content: "访问我的CSDN",
      placement: "left",
      theme: "light-border",
      arrow: true,
    });

    tippy("#to-juejin", {
      content: "访问我的掘金",
      placement: "left",
      theme: "light-border",
      arrow: true,
    });

    tippy("#to-github", {
      content: "访问我的GitHub",
      placement: "left",
      theme: "light-border",
      arrow: true,
    });

    tippy("#to-gitee", {
      content: "访问我的Gitee",
      placement: "left",
      theme: "light-border",
      arrow: true,
    });
  }
}

export default ToolTip;

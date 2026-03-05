---
title: 聊聊纯 CSS 图标
date: 2021-10-31T16:00:00Z
lang: zh
duration: 6min
description: 纯 CSS 图标方案简介与实践建议。
---

[[toc]]

> 这篇文章是对纯 CSS 图标方案的中文整理版。英文原文可见：[/posts/icons-in-pure-css](/posts/icons-in-pure-css)。

## 背景

在前端项目中，图标通常有三类需求：

- 跟随文字大小缩放
- 能随 `currentColor` 变色
- 彩色图标也能直接使用

传统图片方案在“随上下文变色”上不够理想，而纯 CSS 方案可以更灵活。

## 核心思路

将 SVG 转换为 Data URI 后，按图标类型分两种渲染模式：

- 单色图标：使用 `mask` + `background-color: currentColor`
- 彩色图标：使用 `background-image`

这样可以同时兼顾可着色图标与原生彩色图标。

## 示例

```css
.icon {
  width: 1em;
  height: 1em;
  display: inline-block;
}

/* 单色图标 */
.icon-mask {
  mask: var(--icon) no-repeat center / 100% 100%;
  background-color: currentColor;
}

/* 彩色图标 */
.icon-bg {
  background: var(--icon) no-repeat center / 100% 100%;
}
```

## 使用建议

- 在工程内统一图标命名规则（如 `i-collection:name`）
- 单色图标优先走 `mask` 模式
- 彩色图标保留原始颜色，走 `background-image`
- 保持 `1em` 尺寸策略，确保与文本排版一致

## 工具链

可以配合 UnoCSS 的图标预设来自动化管理图标资源与类名。

如果你要查看和搜索图标集合，可使用：

- [Icônes](https://icones.js.org/)

## 总结

纯 CSS 图标并不是替代所有方案，而是为“可缩放、可继承颜色、易工程化”提供了一条稳定路径。
# 首页 + 论坛 AstroPaper 风格 Figma Brief

> 用于在 Figma 中创建 3 个画板：`首页`、`论坛列表`、`论坛详情`

## 1. Design Tokens

### Spacing (8px Grid)
- 4, 8, 12, 16, 24, 32, 48, 64

### Radius
- `sm`: 8
- `md`: 12
- `lg`: 16
- `xl`: 20

### Typography
- `Display`: 40 / 48 / 700
- `H1`: 32 / 40 / 700
- `H2`: 24 / 32 / 700
- `H3`: 20 / 28 / 600
- `Body`: 16 / 28 / 400
- `Body-sm`: 14 / 24 / 400
- `Meta`: 12 / 18 / 500

### Color (Light)
- `bg/base`: #F7F9FB
- `bg/panel`: #FFFFFF
- `text/primary`: #0F172A
- `text/secondary`: #475569
- `text/muted`: #94A3B8
- `border/default`: #E2E8F0
- `accent/primary`: #0D9488
- `accent/primary-soft`: #CCFBF1

### Color (Dark)
- `bg/base`: #070B14
- `bg/panel`: rgba(16, 23, 42, 0.72)
- `bg/panel-strong`: rgba(15, 23, 42, 0.9)
- `text/primary`: #E2E8F0
- `text/secondary`: #CBD5E1
- `text/muted`: #94A3B8
- `border/default`: rgba(148, 163, 184, 0.28)
- `accent/primary`: #2DD4BF
- `accent/primary-soft`: rgba(45, 212, 191, 0.18)

### Motion
- Hover lift: `translateY(-1px ~ -2px)`
- Duration: `150-220ms`
- Easing: `cubic-bezier(0.2, 0.8, 0.2, 1)`

## 2. Artboard A: 首页 (Desktop 1440)

### Layout
- Header (轻量导航)
- Hero（标题 + 副标题 + CTA）
- Recent Posts（3~6 卡片）
- Forum CTA（引导到 `/forum`）
- Footer（低噪声）

### Visual Notes
- 信息密度中低，重点在留白和阅读引导
- 卡片 hover 仅轻微边框/阴影变化

## 3. Artboard B: 论坛列表 (Desktop 1440)

### Layout
- 顶部：标题 + 发布按钮
- 次级：筛选条（Tab + 搜索 + 标签）
- 列表：帖子卡片（日期/作者/标题/摘要/标签/点赞）
- 空态 & 加载态

### Card Spec
- 卡片 padding: 24
- 标题与摘要层级明显，避免按钮抢视觉
- 点赞按钮放在卡片底部左侧，次级强调

## 4. Artboard C: 论坛详情 (Desktop 1440)

### Layout
- 返回按钮（顶部）
- 元信息行（日期/作者/标签）
- 主帖正文（阅读面板）
- 评论列表（紧凑密度）
- 评论编辑器（高度 180）

### Comment Density
- 评论卡片比主帖小一档
- 字号 14，行高 1.65~1.7
- 交互只保留必要操作（点赞、删除）

## 5. Responsive Notes (Mobile 390)
- 首页卡片单列
- 论坛列表筛选区折叠为两行
- 论坛详情目录默认折叠
- 评论区维持紧凑，避免输入器过高


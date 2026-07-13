# PRD — Hand-Painted-icon 手绘图标集

> 版本：v1.0 ｜ 日期：2026-07-13 ｜ 维护者：Hanilbert

## 1. 项目背景

本项目是一套供 **Surge / Quantumult X / Stash / Loon** 等代理工具使用的手绘风格图标集，fork 自 [Semporia/Hand-Painted-icon](https://github.com/Semporia/Hand-Painted-icon)，现独立维护于 [hanilbert/Hand-Painted-icon](https://github.com/hanilbert/Hand-Painted-icon)。

Stash 与 Loon 用户可导入 JSON 图标清单；Surge 与 Quantumult X 用户通过单张图片地址为策略组等配置项设置图标。

### 上游项目的不足（本项目要解决的问题）

| # | 问题 | 现状证据 |
|---|------|---------|
| P1 | **部分需要的图标未绘制** | 缺少若干常用服务/策略组图标（见 §4.1 清单） |
| P2 | **订阅 JSON 覆盖严重不全** | 清理前有 777 个有效图标，`Semporia.json` 仅收录 379 个；`Accommodation`、`Fitness`、`Food-Delivery`、`Rectangular` 四个目录完全未收录 |
| P3 | **订阅 JSON 指向上游仓库** | 所有 URL 指向 `Semporia/Hand-Painted-icon`，与本仓库脱钩，本仓库新增图标无法被订阅到 |
| P4 | **文件命名不规范** | 订阅文件以人名 `Semporia.json` 命名；`Food-Delivery` 目录用连字符而其余目录用下划线；存在 23 个 `.orig.png` 历史副本及 AppleDouble 垃圾文件 |
| P5 | **README 不规范** | 无项目简介与使用说明；Google Suite 链接错误指向 Rounded_Rectangle；无图标预览表；JSON 内 `"Desing By"` 拼写错误 |
| P6 | **纯手工维护，易漏** | 新增图标后需手工编辑 JSON，这是 P2 产生的根本原因 |

## 2. 目标与非目标

### 2.1 目标

1. **全量可订阅**：订阅 JSON 自动覆盖仓库内 100% 图标，URL 指向本仓库
2. **规范化**：统一文件/目录命名规范，清理冗余文件，重写 README
3. **可扩展**：建立"新增图标 → 自动进入订阅"的零成本维护流程（脚本 + CI）
4. **补齐缺失图标**：按需求清单逐步绘制/收录新图标

### 2.2 非目标（本期不做）

- 不做图标在线预览网站（可作为远期迭代）
- 不改变现有图标的绘画风格与画布规格
- 不重绘上游已有图标
- 不支持 SVG / 多分辨率变体

## 3. 用户与使用场景

| 用户 | 场景 |
|------|------|
| Stash / Loon 用户 | 导入 `icons.json` 图标集，为策略组或节点选择图标 |
| Surge / Quantumult X 用户 | 在配置中引用单张图标的 raw URL |
| 配置分享者 | 在分享的配置文件中直接引用单个图标的 raw URL |
| 仓库维护者（本人） | 绘制新图标 → 放入对应目录 → push → 订阅自动更新 |

**核心订阅地址（改名后）**：

```
https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/icons.json
```

## 4. 功能需求

### 4.1 新增图标清单（P1）

新增图标须遵循 §5 的命名与入库规范。当前第一批以维护者已提供的素材为准。

| 图标 | 分类目录 | 状态 |
|------|---------|------|
| IBKR | Universal | 已入库 |

**建议候选**（按同类图标仓库常见需求，供筛选）：小红书✅(已有 XiaoHongShu)、抖音/TikTok、Telegram✅(Social_Media 已有)、ChatGPT、Claude、Gemini、Emby、哔哩哔哩✅(已有 BiliBili)、美团、拼多多、京东、淘宝、支付宝、PayPal、香港/台湾/日本/美国/新加坡地区节点（Rectangular/Rounded_Rectangle 旗帜可覆盖）。

### 4.2 订阅 JSON 重构（P2/P3/P4/P6）

- **FR-1** 订阅文件统一为 `icons.json`；旧文件 `Semporia.json` 在 v1.1 移除
- **FR-2** `icons.json` 由脚本扫描仓库目录自动生成，收录全部 `*.png`（排除 `.orig.png` 与非图标图片）
- **FR-3** 所有 URL 指向 `hanilbert/Hand-Painted-icon` 的 master 分支 raw 地址
- **FR-4** JSON 顶层字段：`name`（Hand Painted Icon）、`description`（修正拼写，注明 Design By Semporia & Hanilbert）、`icons` 数组按 `分类/名称` 排序
- **FR-5** 图标 `name` 带分类信息以避免跨目录重名（如 `Google_Suite/Calendar` 与 `Fitness/Calendar`），具体格式见 ARCHITECTURE.md
- **FR-6** 配置 GitHub Actions：只读工作流负责校验；master 中包含 PNG、生成器或配置变更时，发布工作流自动更新两份清单

### 4.3 仓库规范化（P4/P5）

- **FR-7** `Food-Delivery` 目录更名为 `Food_Delivery`（统一下划线）
- **FR-8** 删除全部 `.orig.png` 历史副本（23 个）与 AppleDouble 等垃圾文件；添加 `.gitignore` 阻止系统垃圾文件再次入库
- **FR-9** 重写 `README.md`：项目简介、订阅地址、支持的客户端及配置方法、分类目录表（含每类数量）、预览图、命名规范、致谢上游、License 说明
- **FR-10** 修复 README 中 Google Suite 错误链接，所有目录链接指向本仓库

## 5. 图标入库规范（对新增图标生效）

- 格式：108 × 108 PNG，带透明通道，与现有图标画风一致
- 文件命名：`Upper_Snake_Case.png`，多单词用下划线分隔，如 `NetEase_Music.png`
- 品牌名保留官方大小写：`BiliBili.png`、`GitHub.png`、`deviantART.png`
- 归入既有 8 个分类目录之一；不确定时放 `Universal`

## 6. 验收标准

| # | 标准 |
|---|------|
| A1 | `icons.json` 条目数 == 仓库内有效 PNG 总数（当前含新增 IBKR 共 778 个） |
| A2 | 随机抽取 10 条 URL 全部可访问（HTTP 200） |
| A3 | Stash 与 Loon 实测整包导入；Surge 与 Quantumult X 实测单图地址可显示 |
| A4 | 新增一个测试图标并 push 后，CI 自动更新 `icons.json` 且包含该图标 |
| A5 | 仓库内无 `.orig.png`、无 `.DS_Store` 类文件 |
| A6 | README 目录链接指向本仓库，所有使用示例使用本仓库资源地址 |

## 7. 里程碑

| 版本 | 内容 | 对应任务 |
|------|------|---------|
| v1.0 | 仓库规范化 + icons.json 全量生成 + CI 自动化 + README 重写 | TASKS.md M1–M3 |
| v1.1 | 移除 Semporia.json；补齐第一批缺失图标 | TASKS.md M4 |
| v2.0（远期） | 图标在线预览页（GitHub Pages） | 未排期 |

## 8. 风险

| 风险 | 影响 | 对策 |
|------|------|------|
| 删除 `Semporia.json` 导致旧订阅失效 | 已使用旧地址的用户断更 | README 明确公告迁移到 `icons.json` |
| `Food-Delivery` 目录改名导致外部直链失效 | 引用单图 URL 的配置失效 | 独立仓库刚起步、外部引用极少，README 中注明 |
| CI 自动 commit 触发循环 | Actions 死循环 | workflow 内跳过 bot 提交 / 仅在 png 变更时触发 |

# ARCHITECTURE — Hand-Painted-icon 技术架构

> 版本：v1.0 ｜ 日期：2026-07-13 ｜ 配套文档：[PRD.md](PRD.md) / [TASKS.md](TASKS.md)

## 1. 总体设计

本项目本质是一个 **静态资源仓库 + 自动生成的订阅清单**，无服务端、无构建产物依赖。架构目标只有一个：**图标文件是唯一事实来源（Single Source of Truth），订阅 JSON 永远由它派生，绝不手工编辑。**

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Repo: hanilbert/Hand-Painted-icon (master)      │
│                                                         │
│  分类目录/*.png ──┐                                      │
│                  │  scripts/generate_icons.py (扫描)     │
│                  ▼                                      │
│              icons.json  ◄── GitHub Actions 自动生成     │
└──────────────────┬──────────────────────────────────────┘
                   │ raw.githubusercontent.com
          ┌────────┴────────┐
          ▼                 ▼
  Stash / Loon 整包导入   Surge / QuanX 单图引用
```

## 2. 目录结构（目标态）

```
Hand-Painted-icon/
├── Accommodation/          # 住宿类 (47)
├── Fitness/                # 健身类 (47)
├── Food_Delivery/          # 外卖类 (33)  ← 由 Food-Delivery 改名
├── Google_Suite/           # Google 套件 (23)
├── Rectangular/            # 矩形国旗 (264)
├── Rounded_Rectangle/      # 圆角矩形国旗 (262)
├── Social_Media/           # 社交媒体 (69)
├── Universal/              # 通用/代理策略类 (33)
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── TASKS.md
├── scripts/
│   └── generate_icons.py   # 订阅 JSON 生成器
├── iconset.config.json     # 分类、仓库、画布与输出配置
├── .github/
│   └── workflows/
│       ├── validate-icons.yml
│       └── update-icons-json.yml
├── .gitignore
├── icons.json              # 订阅清单（生成物，勿手改）
├── Hand-Painted-icon.png   # README 预览大图
└── README.md
```

**约定**：
- 仅 `iconset.config.json` 明确列出的目录属于图标分类，避免误收预览或素材目录
- 新增分类必须同时更新配置，分类顺序也以配置为准

## 3. 订阅 JSON 格式

`icons.json` 延续上游图标集的最小结构，供 Stash / Loon 导入并保持社区兼容：

```json
{
    "name": "Hand Painted Icon",
    "description": "Hand-painted icon set. Design by Semporia, maintained by Hanilbert.",
    "icons": [
        {
            "name": "Universal - Netflix",
            "url": "https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/Universal/Netflix.png"
        }
    ]
}
```

### 设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| `name` 格式 | `分类 - 图标名`（下划线转空格） | 全库有跨目录重名（如 `Calendar` 同时存在于 Google_Suite 和 Fitness；国旗在 Rectangular/Rounded_Rectangle 成对出现 262 个），纯文件名会在客户端列表中无法区分 |
| 排序 | 先按分类、再按图标名字典序 | 生成结果稳定，diff 可读，客户端列表可预期 |
| `time` 字段 | 移除 | 每次生成都变化会产生无意义 diff；生成时间由 git commit 记录 |
| 过滤规则 | 仅收录 `*.png`，排除 `*.orig.png`、根目录预览图 `Hand-Painted-icon.png`、隐藏文件 | 保证清单纯净 |
| 分支 | 固定 `master` | 与现有 raw URL 习惯一致 |

## 4. 生成脚本 `scripts/generate_icons.py`

**技术选型：Python 3.11+ 标准库**。CI 固定使用 Python 3.13；本地环境需自行提供 Python 3，不依赖操作系统预装。

职责与行为：

```
输入:  iconset.config.json 与配置列出的分类目录
处理:  1. 递归收集配置目录中的 *.png
       2. 校验 PNG、108×108 画布、透明通道、隐藏文件与历史副本
       3. 检查显示名和 URL 重复，逐段编码 URL
       4. 按配置中的分类顺序和文件名字典序稳定排序
输出:  icons.json（UTF-8，4 空格缩进）
退出码: 0 = 成功；同时打印统计（每分类数量/总数），供 CI 日志检查
```

可选参数：`--check`——校验清单是否与目录状态一致但不写文件，供 CI 和本地检查使用。

## 5. CI 工作流

```yaml
validate-icons.yml:
  pull request: 使用 --check 拦截图片或清单不一致
  master push: 重新生成后校验图片和输出
  权限: contents: read

update-icons-json.yml:
  master 的 PNG、生成器或配置变化时重新生成清单
  只有实际变化才以 github-actions[bot] 提交，冲突时同步后重试一次
  权限: contents: write；同一时间只允许一个发布任务
```

自动提交信息固定为 `chore: 自动更新图标订阅`。机器人提交只包含 `icons.json`，且使用仓库令牌产生的提交不会再次触发普通 push 工作流。

## 6. 兼容与迁移策略

| 阶段 | Semporia.json | icons.json |
|------|--------------|-----------|
| v1.0 | 保留但冻结，内容与正式清单同步 | 上线，README 主推 |
| v1.1 | 已删除 | 唯一订阅入口 |

`Food-Delivery → Food_Delivery` 改名使用 `git mv` 保留历史；旧路径直链会 404，在 README 的 Changelog 中注明。

## 7. 质量保障

- **一致性门禁**：CI 中 `--check` 模式保证清单与目录一致
- **素材门禁**：生成器拒绝损坏图片、非 108 × 108 画布、缺少透明通道、重复条目和历史副本
- **URL 可用性抽检**：验收时用 `curl` 抽样 10 条（见 PRD A2），不进 CI（避免对 raw.githubusercontent 频繁请求）
- **命名规范**：README 中明文约定 `Upper_Snake_Case.png`；暂不做自动 lint（图标量小、人工可控），若后续违规频发再在 CI 中加校验
- **`.gitignore`**：屏蔽 `.DS_Store`、`._*`、`Thumbs.db`

## 8. 远期演进（不在本期）

- GitHub Pages 图标预览画廊（读 icons.json 渲染，零额外数据源）
- WebP/多分辨率变体（需评估客户端兼容性）
- 按分类拆分多个订阅 JSON（如 `icons-flags.json`），供只需国旗的用户减小订阅体积

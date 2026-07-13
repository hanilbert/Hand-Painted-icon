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
│              icons.json  ◄── GitHub Actions 自动再生成   │
└──────────────────┬──────────────────────────────────────┘
                   │ raw.githubusercontent.com
                   ▼
      Surge / Quantumult X / Stash / Loon（订阅方）
```

## 2. 目录结构（目标态）

```
Hand-Painted-icon/
├── Accommodation/          # 住宿类 (50)
├── Fitness/                # 健身类 (49)
├── Food_Delivery/          # 外卖类 (50)  ← 由 Food-Delivery 改名
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
├── .github/
│   └── workflows/
│       └── update-icons-json.yml
├── .gitignore
├── icons.json              # 订阅清单（生成物，勿手改）
├── Semporia.json           # 旧订阅（v1.1 移除）
├── Hand-Painted-icon.png   # README 预览大图
└── README.md
```

**约定**：
- 根目录下所有「首字母大写的目录」均视为图标分类目录，脚本自动发现，新增分类无需改代码
- `docs/`、`scripts/`、`.github/` 为小写，天然与分类目录区分

## 3. 订阅 JSON 格式

Surge / QuanX 图标订阅的事实标准格式（与上游一致，保持兼容）：

```json
{
    "name": "Hand Painted Icon",
    "description": "Hand-painted icon set for Surge / Quantumult X. Design by Semporia, maintained by Hanilbert.",
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

**技术选型：Python 3 标准库**（macOS 自带 python3，零依赖；仓库无 Node 生态，不引入 package.json）。

职责与行为：

```
输入:  仓库根目录（脚本按自身位置定位，无需传参）
处理:  1. 发现分类目录（根目录下首字母大写的目录）
       2. 递归收集 *.png，应用过滤规则
       3. URL 编码文件路径（防御空格等特殊字符）
       4. 按 (分类, 文件名) 排序
输出:  icons.json（UTF-8，4 空格缩进，与上游格式对齐）
退出码: 0 = 成功；同时打印统计（每分类数量/总数），供 CI 日志检查
```

可选参数：`--check`——只校验 icons.json 是否与目录状态一致（不写文件），供 CI/pre-commit 做一致性门禁。

## 5. CI 工作流 `.github/workflows/update-icons-json.yml`

```yaml
触发:  push 到 master，且路径匹配 ['**.png', 'scripts/**']
步骤:  checkout → 运行 generate_icons.py → 若 icons.json 有 diff
       则以 github-actions[bot] 身份 commit & push
防环:  仅当 icons.json 有实际变更才提交；bot 提交只改 icons.json，
       不含 png，不会再次触发（路径过滤天然防环）
权限:  contents: write（使用内置 GITHUB_TOKEN，无需额外 secret）
```

提交信息固定为 `chore: 自动更新 icons.json`。

## 6. 兼容与迁移策略

| 阶段 | Semporia.json | icons.json |
|------|--------------|-----------|
| v1.0 | 保留但冻结（内容替换为与 icons.json 相同、URL 指向本仓库，顶部 description 注明已迁移） | 上线，README 主推 |
| v1.1 | 删除 | 唯一订阅入口 |

`Food-Delivery → Food_Delivery` 改名使用 `git mv` 保留历史；旧路径直链会 404，在 README 的 Changelog 中注明。

## 7. 质量保障

- **一致性门禁**：CI 中 `--check` 模式保证 icons.json 与目录永不脱节
- **URL 可用性抽检**：验收时用 `curl` 抽样 10 条（见 PRD A2），不进 CI（避免对 raw.githubusercontent 频繁请求）
- **命名规范**：README 中明文约定 `Upper_Snake_Case.png`；暂不做自动 lint（图标量小、人工可控），若后续违规频发再在 CI 中加校验
- **`.gitignore`**：屏蔽 `.DS_Store`、`._*`、`Thumbs.db`

## 8. 远期演进（不在本期）

- GitHub Pages 图标预览画廊（读 icons.json 渲染，零额外数据源）
- WebP/多分辨率变体（需评估客户端兼容性）
- 按分类拆分多个订阅 JSON（如 `icons-flags.json`），供只需国旗的用户减小订阅体积

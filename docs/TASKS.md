# TASKS — Hand-Painted-icon 任务拆分

> 版本：v1.0 ｜ 日期：2026-07-13 ｜ 配套文档：[PRD.md](PRD.md) / [ARCHITECTURE.md](ARCHITECTURE.md)
>
> 状态标记：`[ ]` 待办 ｜ `[~]` 进行中 ｜ `[x]` 完成
> 每个任务 = 一次原子提交，提交信息见各任务 `commit:` 行。

## M1 仓库规范化（v1.0 前置）

- [x] **T1.1 清理垃圾文件**
  删除已跟踪的 `._.DS_Store`（含 `Social_Media/._.DS_Store`、根目录已 D 的那个），新增 `.gitignore`（`.DS_Store` / `._*` / `Thumbs.db`）
  commit: `chore: 清理 macOS 垃圾文件并添加 .gitignore`
  依赖：无

- [x] **T1.2 删除 .orig.png 冗余文件**
  删除全部 23 个 `.orig.png` 历史副本（Accommodation×3、Food-Delivery×17、Universal×1、Fitness×2）
  commit: `chore: 删除 .orig.png 冗余源文件`
  依赖：无

- [x] **T1.3 目录改名 Food-Delivery → Food_Delivery**
  使用 `git mv` 保留历史；全库 grep 确认无残留引用
  commit: `refactor: 统一目录命名，Food-Delivery 改为 Food_Delivery`
  依赖：T1.2（避免改名后再删文件产生两次 rename）

## M2 订阅 JSON 自动化（v1.0 核心）

- [ ] **T2.1 编写生成脚本 scripts/generate_icons.py**
  按 ARCHITECTURE.md §4 实现：自动发现分类目录、过滤规则、`分类 - 名称` 命名、URL 编码、稳定排序、`--check` 模式
  commit: `feat: 新增 icons.json 生成脚本`
  依赖：T1.1–T1.3（目录状态定型后再生成）

- [ ] **T2.2 生成 icons.json 并本地验证**
  运行脚本生成 `icons.json`；验证条目数 == 有效 PNG 数（约 790）；`curl` 抽检 10 条 URL 返回 200；JSON 语法校验
  commit: `feat: 生成全量订阅文件 icons.json（覆盖 8 分类约 790 图标）`
  依赖：T2.1

- [ ] **T2.3 冻结 Semporia.json（兼容过渡）**
  内容替换为与 icons.json 一致、URL 指向本仓库，description 注明"已迁移至 icons.json"
  commit: `fix: 修正 Semporia.json 指向本仓库并标记迁移`
  依赖：T2.2

- [ ] **T2.4 配置 GitHub Actions 自动更新**
  新增 `.github/workflows/update-icons-json.yml`（按 ARCHITECTURE.md §5：png 路径触发、diff 才提交、路径过滤防环）
  commit: `ci: 新增 icons.json 自动更新工作流`
  依赖：T2.1

- [ ] **T2.5 端到端验证 CI**
  push 一个测试 png（或改动现有 png 的 touch 提交）→ 确认 bot 自动提交更新了 icons.json → 移除测试文件
  commit: 无（验证性任务，产生的提交由 CI 生成）
  依赖：T2.4，且仓库已 push 到 GitHub

## M3 文档重写（v1.0 收尾）

- [ ] **T3.1 重写 README.md**
  按 PRD FR-9/FR-10：项目简介、订阅地址（icons.json）、Surge/QuanX/Stash/Loon 配置方法、分类目录表（含数量）、预览图、命名规范、迁移公告（Semporia.json 弃用计划 + Food_Delivery 改名说明）、致谢上游
  commit: `docs: 重写 README，规范项目说明与订阅指引`
  依赖：T2.2（订阅地址已生效）

- [ ] **T3.2 在 Surge / Quantumult X 实机验收**
  两个客户端实测订阅 → 记录结果到 PR/commit 描述；对应 PRD 验收 A3
  commit: 无（验收任务）
  依赖：T3.1

## M4 缺失图标补齐（v1.1）

- [ ] **T4.1 确定新增图标清单**
  填充 PRD §4.1 占位表：确定名称、分类、优先级
  commit: `docs: 补充新增图标需求清单`
  依赖：无（可与 M1–M3 并行）

- [ ] **T4.2 绘制/收录第一批图标**
  按 PRD §5 入库规范逐个入库；每个图标一次提交，CI 自动更新订阅
  commit: `feat: 新增 <分类>/<图标名> 图标`（逐个）
  依赖：T4.1、T2.4

- [ ] **T4.3 移除 Semporia.json**
  过渡期结束（建议 icons.json 上线 1 个月后）删除旧订阅文件，README 更新
  commit: `chore!: 移除已弃用的 Semporia.json 订阅文件`
  依赖：T2.3、T3.1

## 执行顺序总览

```
T1.1 ─┐
T1.2 ─┼─ T1.3 ── T2.1 ── T2.2 ─┬─ T2.3 ── T4.3
      │                        ├─ T3.1 ── T3.2
      │          T2.1 ── T2.4 ─┴─ T2.5
T4.1 ─┴──────────────────────────  T4.2（依赖 T4.1 + T2.4）
```

**关键路径**：T1.3 → T2.1 → T2.2 → T3.1 → T3.2（约 1 个工作日可完成 v1.0）

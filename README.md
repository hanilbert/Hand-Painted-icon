# Hand-Painted-icon

一套供代理工具策略组、节点和规则使用的手绘风格 PNG 图标集。项目源自 [Semporia/Hand-Painted-icon](https://github.com/Semporia/Hand-Painted-icon)，现由 Hanilbert 独立维护。

![图标预览](Hand-Painted-icon.png)

## 图标清单

全量清单包含 8 个分类、780 个图标。正式地址：

```text
https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/icons.json
```

图标文件和清单均从 `master` 分支提供。清单由仓库内图片自动生成，新图标合入后会自动进入清单。

## 使用方式

不同客户端提供的图标能力并不完全相同。

### Stash

可使用 Stash 的图标集导入入口：

[一键导入 Stash](https://link.stash.ws/install-icon-set/raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/icons.json)

也可以在策略组中直接填写单张 PNG 地址：

```yaml
proxy-groups:
  - name: 自动选择
    type: url-test
    icon: https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/Universal/Auto_Speed.png
```

### Loon

可使用 Loon 的统一链接导入图标集：

[一键导入 Loon](https://www.nsloon.com/openloon/import?iconset=https%3A%2F%2Fraw.githubusercontent.com%2Fhanilbert%2FHand-Painted-icon%2Fmaster%2Ficons.json)

### Surge

Surge 使用单张图标地址。以下写法适用于支持 `icon-url` 的版本：

```ini
自动选择 = select, ProxyA, ProxyB, icon-url=https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/Universal/Select.png
```

### Quantumult X

Quantumult X 使用单张图标地址：

```ini
[policy]
static = 自动选择, ProxyA, ProxyB, img-url=https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/Universal/Select.png
```

> Stash 与 Loon 有官方图标集导入入口；Surge 与 Quantumult X 的公开资料确认的是单张图片引用。完整清单仍需在各客户端当前版本中实际导入后，才能确认条目上限和刷新行为。

## 分类

| 分类 | 数量 | 内容 |
|---|---:|---|
| [Accommodation](Accommodation) | 47 | 住宿与酒店设施 |
| [Fitness](Fitness) | 47 | 健身与运动 |
| [Food_Delivery](Food_Delivery) | 33 | 餐饮与外卖 |
| [Google_Suite](Google_Suite) | 23 | Google 服务 |
| [Rectangular](Rectangular) | 264 | 矩形地区旗帜 |
| [Rounded_Rectangle](Rounded_Rectangle) | 262 | 圆角地区旗帜 |
| [Social_Media](Social_Media) | 70 | 社交媒体与网络服务 |
| [Universal](Universal) | 34 | 通用策略与其他服务 |
| **合计** | **780** | |

## 单张图标地址

单张图标使用以下格式：

```text
https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/<分类>/<文件名>.png
```

例如：

```text
https://raw.githubusercontent.com/hanilbert/Hand-Painted-icon/master/Universal/IBKR.png
```

## 新增图标规范

- 使用带透明背景的 108 × 108 PNG。
- 文件名采用英文；多个单词以下划线连接，例如 `NetEase_Music.png`。
- 品牌名可保留官方写法，例如 `GitHub.png`。
- 图标放入现有分类；无法确定时放入 `Universal`。
- 新增或修改后运行 `python3 scripts/generate_icons.py`，再运行 `python3 scripts/generate_icons.py --check` 检查结果。

## 来源

感谢 [Semporia](https://github.com/Semporia) 创建原始图标集。

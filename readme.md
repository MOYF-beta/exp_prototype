# 深度学习实验项目规范化模板

本仓库是一个**实验项目骨架**，意在提供标准化的目录结构、代码组织方式和实验运行规范。使用方式：

```bash
git clone https://github.com/MOYF-beta/exp_prototype.git exp_prototype
cd exp_prototype
git remote set-url origin <your-own-remote>
git push -u origin main
```

 `data/`、`raw_weights/` 等大文件目录可以替换为软链接，`ref/` 中放入参考论文与代码，填充自己的模型、数据集、训练器代码即可开始实验。当前各目录代码均为空的占位，请在开始实验后更新此 README 文档
---

## 目录结构

这里展示的结构是一种基于清晰、严谨与可追踪、复现原则的最优实践，并非强制要求。

```
# .
# ├── data/                                          # 数据集目录，建议用软链接指向实际存储位置
# │   └── this_folder_can_be_a_link
# ├── docs/                                          # 文档与论文源码
# │   ├── latex/                                     #   LaTeX 论文工程
# │   │   ├── img/                                   #     论文插图
# │   │   ├── cite.bib                               #     参考文献
# │   │   └── paper.tex                              #     论文正文
# │   ├── design.md                                  #   方案设计文档
# │   ├── some_bugs.md                               #   Bug 记录
# │   └── some_note.md                               #   实验笔记 / 杂记
# ├── exp_scripts/                                   # 实验启动入口（按实验路线分目录）
# │   ├── route_abc/                                 #   实验路线 ABC
# │   └── route_xyz/                                 #   实验路线 XYZ
# │       ├── launch.py                              #     启动脚本，组装 trainer + config
# │       └── params.yaml                            #     声明式训练配置
# ├── output/                                        # 所有实验产出（一次运行一个子目录）
# │   └── run_{name}_{time}_{param}/                 #   单次运行目录，命名唯一可辨识
# │       ├── checkpoints/                           #     模型检查点（按 epoch 分目录）
# │       │   └── 1/                                 #       epoch-1
# │       │       ├── model.pth                      #         模型权重
# │       │       └── optimizer.pth                  #         优化器状态
# │       ├── epochs/                                #     每 epoch 评估产出
# │       │   └── 1/                                 #       epoch-1
# │       │       ├── img_gt/                        #         GT / 可视化图像
# │       │       ├── compare.png                    #         对比图
# │       │       └── eval.jsonl                     #         评估指标（每行一条记录）
# │       ├── git_status/                            #     运行时 git 快照，确保代码可追溯
# │       │   ├── uncommited_files/                  #        未提交文件的 patch
# │       │   │   └── patch.py
# │       │   └── commit.txt                         #        当前 HEAD commit hash
# │       ├── other_logging_files.tensorboard.wandb  #   TensorBoard / W&B 日志
# │       ├── run_param.yaml                         #   本次运行实际使用的完整参数
# │       └── stdout+stderr.log                      #   完整控制台输出
# ├── raw_weights/                                   # 预训练权重，建议用软链接
# │   └── this_folder_can_be_a_link
# ├── ref/                                           # 外部参考资料
# │   ├── repo/                                      #   参考代码仓库
# │   └── paper/                                     #   参考论文
# ├── src/                                           # 所有源代码
# │   ├── datasets/                                  #   数据集模块
# │   │   └── dataset_a/                             #     单个数据集：dataset + dataloader
# │   │       ├── dataloader_a.py
# │   │       ├── dataset_a1.py
# │   │       └── dataset_a2.py
# │   ├── models/                                    #   模型模块（每个模型一个子目录）
# │   │   ├── model_xxx/
# │   │   └── model_yyy/
# │   ├── trainers/                                  #   训练器 & 损失函数
# │   │   ├── loss_qwe.py
# │   │   └── trainer_aaa.py
# │   └── utils.py                                   #   跨模块共享工具函数
# └── readme.md
```

## 最佳实践约定

### 源码组织（`src/`）

各子模块遵循"关注点分离"原则，按数据类型和功能拆分，避免单一巨大文件：

| 模块 | 目录 | 约定 |
|------|------|------|
| 模型 | `src/models/model_xxx/` | 每个模型独立目录，可含多个 `.py` 子模块 |
| 数据集 | `src/datasets/dataset_a/` | 包含 `dataset_*.py`（数据类）+ `dataloader_*.py`（加载器） |
| 训练器 | `src/trainers/` | `trainer_*.py`（训练循环）+ `loss_*.py`（损失函数），灵活组合 |
| 工具 | `src/utils.py` | 全局共享的辅助函数 |

核心原则：

- **数据与逻辑分离**：`dataset_a1.py` 定义数据读取与预处理，`dataloader_a.py` 负责批处理与采样逻辑，便于针对同一数据集切换不同加载策略
- **模型与训练解耦**：`models/` 只定义网络结构，`trainers/` 负责训练循环与优化逻辑，两者可自由组合
- **损失函数独立**：`loss_*.py` 与 `trainer_*.py` 分离，同一损失可用于不同 trainer，同一 trainer 可切换不同损失

### 实验路线（`exp_scripts/`）

- **一路线一目录**：每条实验路线映射为一个 `route_xxx/`，建议按逻辑维度命名区分，例如按模型架构（`route_resnet` / `route_vit`）、技术路线（`route_baseline` / `route_finetune`）、或消融变量（`route_ablation_loss`）等，避免参数混入命令行脚本造成不可追溯
- **声明式配置**：`params.yaml` 承载所有可变参数（数据、模型、超参、分阶段调度），不在代码中硬编码
- **启动脚本极简化**：`launch.py` 只做三件事 — 转储本次运行的实际参数（`run_param.yaml`）→ 记录当前 git 状态（`git_status/`）→ 调用 trainer 并将 stdout/stderr 重定向到日志文件。训练过程的日志输出由 trainer 自身负责
  - **⚠️ 必须使用 `subprocess.run` 调用训练入口**，不要直接 `import` 后调用 trainer 方法。只有通过子进程运行，才能正确捕获 stdout/stderr 并重定向到日志文件，同时也避免子进程的异常污染主进程

### 参数配置（`params.yaml`）

`params.yaml` 是每条实验路线的唯一配置入口，承载训练过程中所有可变参数。一律使用声明式写法，不在 `launch.py` 或 trainer 中硬编码任何超参。

一个典型的 `params.yaml` 包含以下区块（参见 `exp_scripts/route_xyz/params.yaml`）：

| 区块 | 职责 | 示例字段 |
|------|------|----------|
| **基础配置** | 实验标识、随机种子、GPU 分配 | `exp_name`、`seed`、`GPU` |
| **数据集** | 数据路径及预处理参数 | `root`、augmentation、采样比、分辨率、train/val split |
| **模型** | 模型架构定义及预训练权重路径 | `path`（预训练权重）、各子模块的架构参数 |
| **训练调度** | 全局 epoch 数与评估/保存频率 | `epochs`、`eval_frequency`、`save_frequency`、`eval_before_training` |
| **分模块调度**（`parts`） | 各子模块独立的冻结、预热与学习率策略 | `freeze_epochs`、`warmup_epochs`、`lr`，按模块名分节 |
| **优化器** | 优化器类型、batch size、权重衰减、学习率调度器 | `batch_size`、`weight_decay`、scheduler 参数 |
| **损失函数** | 损失类型及多损失权重 | 损失类型、各损失项的权重系数 |
| **杂项** | 特定实验的额外 trick 和可变参数 | 任何未归入以上区块的临时代码开关 |

关键原则：

- **分模块调度**：`parts` 是 `params.yaml` 最具特色的设计。每个模型子模块（如 `head_xx`、`body_zz`）可独立配置 `freeze_epochs`（前 N 轮冻结）、`warmup_epochs`（前 N 轮线性预热）和 `lr`（独立学习率），实现差异化训练策略而无需修改模型代码
- **参数说明即文档**：值未确定的字段用注释占位（如 `# type, weight_decay, scheduler, etc.`），后续填入具体值时删除注释即可，始终保持配置可读
- **`...` 占位符**：文件末尾的 `...` 表明配置可随实验需求自由扩展，不必拘泥于固定字段
- **参数覆盖约定**：命令行传入的参数应覆盖 `params.yaml` 中的同名项，最终生效值均写入 `run_param.yaml` 存档

### 输出管理（`output/`）

- **一次运行一个目录**：命名格式 `run_{name}_{time}_{param}` 保证目录名唯一可辨识，避免结果互相覆盖
- **Git 快照是刚性约束**：每次运行必须记录 `git_status/commit.txt` 和 `uncommited_files/`，这是可追溯性的底线。未提交的修改不应进入实验 — 若确有必要，patch 会自动保存
- **评估结果与检查点按 epoch 分目录**：便于按时间点检索和对比，避免单一大文件堆砌
- **参数即时快照**：运行启动时立刻保存 `run_param.yaml`（含命令行覆盖后的最终参数），防止事后遗忘

### `data/` 与 `raw_weights/` 的管理

这两类资源通常体积较大且不应进入 Git，推荐使用**软链接**指向实际存储位置。这样仓库本身保持轻量，同时代码中的相对路径仍可正常工作。

`.gitignore` 中应添加：

```gitignore
# 大型外部资源（通常为软链接）
data/
raw_weights/

# Python 运行时
__pycache__/
*.pyc
*.pyo

# 虚拟环境
.venv/
venv/
conda_env/

# IDE
.vscode/
.idea/
```

---

## 输出目录解读

一次运行的输出目录 `output/run_{name}_{time}_{param}/` 包含：

| 文件/目录 | 用途 |
|-----------|------|
| `run_param.yaml` | 本次运行实际生效的参数，用于结果复现 |
| `stdout+stderr.log` | 完整终端输出，便于回溯排查 |
| `checkpoints/{epoch}/` | 按 epoch 编号保存 `model.pth` + `optimizer.pth`，支持断点续训 |
| `epochs/{epoch}/` | 按 epoch 输出的评估结果（`eval.jsonl`）和可视化（`compare.png`、`img_gt/`） |
| `git_status/` | 运行时 git 快照（commit hash + 未提交 patch），确保代码可追溯 |
| `other_logging_files.*` | TensorBoard / W&B 等第三方日志 |

---

## 可复现性保障

本模板的设计围绕一个核心目标：**任何实验结果都可以完整复现**。这一目标通过三重机制实现，每项机制都直接映射到 `output/run_xxx/` 目录中的对应产物：

1. **代码快照** — `git_status/commit.txt` 记录运行时的 commit hash，`uncommited_files/` 以 patch 形式保存所有未提交的修改。这意味着即使实验在非干净 git 状态下运行，当时的代码也能完整还原
2. **参数快照** — `run_param.yaml` 在运行启动时立刻保存本次运行的全部参数（含命令行覆盖项），杜绝事后遗忘参数配置的可能
3. **完整日志** — `stdout+stderr.log` 捕获训练全过程的控制台输出，`eval.jsonl` 以标准化 JSONL 格式逐条记录每个 epoch 的评估指标，便于程序化分析和对比

> 只要保留 `output/run_xxx/` 目录，任何结果都可以追溯回当时的代码、参数和完整运行日志。

---

## 磁盘空间管理

实验产出（模型权重、优化器状态、日志）会快速消耗磁盘空间，以下是一些节约策略：

- **区分外部资源与内部产出**：外部资源（`data/`、`raw_weights/`）允许使用软链接指向其他存储位置；内部产出（`output/` 下的模型、checkpoint、日志等）**禁止软链接**，必须保存在当前目录中，这是可复现性的底线。因此整个实验目录应放置在磁盘空间充足的分区上
- **只保留最新优化器状态**：在 `params.yaml` 中设置 `only_keep_latest_optimizer: true`，仅保留最近一个 epoch 的 `optimizer.pth`。模型权重（`model.pth`）仍按 epoch 全量保留。优化器状态体积通常与模型权重相当甚至更大，这一项即可节省约 50% 的 checkpoint 空间
- **定期清理无用 checkpoint**：确认不再需要的旧 run 目录可以直接删除；对仍需保留的 run，可删除中间 epoch 的 `optimizer.pth`
- **虚拟环境置于项目内**：将 conda 环境或 venv 创建在实验目录下（如 `./conda_env/` 或 `./.venv/`），一方面确保环境与项目绑定、便于复现，另一方面避免 `~/.conda/` 或系统目录被占满。记得将环境目录加入 `.gitignore`

```bash
# 在项目内创建 conda 环境
conda create -p ./conda_env python=3.10 -y
conda activate ./conda_env

# 或在项目内创建 venv
python -m venv .venv
source .venv/bin/activate
```

---

## 论文写作

论文 LaTeX 源码在 `docs/latex/`，与实验代码同仓库管理：

- `paper.tex` — 正文
- `cite.bib` — 参考文献
- `img/` — 插图目录

推荐工作流：实验中产出的图表直接输出到 `docs/latex/img/`，保持论文插图与实验结果的同步。

---

## 其他文档

- [EXP.md](./EXP.md) — 面向实验员的常用命令、调试技巧等杂项记录
- `docs/design.md` — 项目方案设计
- `docs/some_bugs.md` — 已发现的 Bug 及处理方式
- `docs/some_note.md` — 实验过程中零散的想法和笔记
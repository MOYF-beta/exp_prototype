# 实验员操作手册 (EXP.md)

面向日常实验操作的常用命令、调试技巧与杂项备忘。

---

## 环境初始化

```bash
# 克隆骨架并绑定到自己的远程仓库
git clone <this-repo> my_experiment && cd my_experiment
git remote set-url origin git@github.com:your-team/your-project.git
git push -u origin main

# 创建虚拟环境（以 conda 为例）
conda create -n exp python=3.10 -y && conda activate exp
pip install -r requirements.txt   # 如果有的话
```

---

## 数据与权重管理

```bash
# 挂载数据集（软链接）
rm -rf data
ln -s /mnt/data/your_dataset data

# 挂载预训练权重
rm -rf raw_weights
ln -s /mnt/weights/pretrained raw_weights

# 验证链接
ls -la data raw_weights
```

---

## 实验操作

### 新建实验路线

```bash
# 从已有模板复制
cp -r exp_scripts/route_xyz exp_scripts/route_${YOUR_EXP_NAME}
# 编辑 params.yaml 和 launch.py
```

### 启动训练

```bash
# 单次运行
python exp_scripts/route_myexp/launch.py

# 后台运行并记录日志
nohup python exp_scripts/route_myexp/launch.py > output/run_myexp_$(date +%Y%m%d_%H%M%S)/stdout+stderr.log 2>&1 &

# 使用 screen / tmux 保持会话
screen -S myexp
python exp_scripts/route_myexp/launch.py
# Ctrl+A D 断开，screen -r myexp 恢复
```

### 批量参数扫描

```bash
# 遍历不同 random seed
for seed in 42 123 456 789; do
    python exp_scripts/route_myexp/launch.py --seed $seed
done

# 或用 GNU Parallel
parallel python exp_scripts/route_myexp/launch.py --lr ::: 0.001 0.0005 0.0001
```

---

## 监控与调试

### 查看训练进度

```bash
# 实时看日志尾部
tail -f output/run_xxx/stdout+stderr.log

# 看最新 eval 结果
cat output/run_xxx/epochs/*/eval.jsonl | tail -20

# 用 jq 解析 eval.jsonl
cat output/run_xxx/epochs/10/eval.jsonl | jq .
```

### GPU 监控

```bash
watch -n 1 nvidia-smi
# 或使用 nvitop（推荐）
pip install nvitop && nvitop
```

### 磁盘空间

```bash
# 检查 output 目录占用
du -sh output/
du -sh output/run_* | sort -rh | head -10

# 清理旧 checkpoint（保留模型权重、删除优化器状态可大幅节省空间）
find output/ -name "optimizer.pth" -mtime +30 -delete
```

---

## Git 操作规范

### 提交前检查

```bash
# 实验代码修改后，确保提交再运行
git status
git diff --stat   # 看改动概览
git add src/ exp_scripts/
git commit -m "feat: add model_xxx and route_myexp"
```

### 实验后追溯

```bash
# 查看某次运行的代码版本
cat output/run_xxx/git_status/commit.txt

# 还原到当时的代码状态
git checkout $(cat output/run_xxx/git_status/commit.txt)

# 应用未提交的 patch（如果有）
git apply output/run_xxx/git_status/uncommited_files/patch.py
```

---

## 常见问题

### 显存不足 (OOM)

1. 减小 `batch_size`
2. 启用梯度累积
3. 使用混合精度训练 (AMP)
4. 检查是否有内存泄漏（`watch -n 1 nvidia-smi` 看显存趋势）

### 训练不收敛

1. 先用小数据过拟合测试（验证 pipeline 正确性）
2. 检查 `eval_before_training: true` 下的初始指标
3. 对比 `run_param.yaml` 与基线配置的差异

### NaN Loss

1. 降低学习率
2. 检查数据是否有异常值
3. 添加梯度裁剪
4. 使用 `torch.autograd.set_detect_anomaly(True)` 定位

### 磁盘写满

```bash
# 紧急清理：删除最旧的 N 个 run 目录
ls -t output/ | tail -n +50 | xargs -I {} rm -rf output/{}

# 日常：在 launch.py 中设置 only_keep_latest_optimizer: true
# 定期清理 optimizer.pth（通常只用于断点续训）
```

---

## 杂项备忘

### TensorBoard

```bash
tensorboard --logdir output/ --port 6006
# 浏览器打开 http://localhost:6006
```

### W&B (Weights & Biases)

```bash
wandb login
# 在 params.yaml 或 launch.py 中配置 project/entity
```

### 快速对比多次实验

```bash
# 提取所有运行的最终 eval 指标
for d in output/run_*/; do
    echo -n "$d: "
    cat "$d/epochs/"*/eval.jsonl 2>/dev/null | tail -1
done
```

### 论文图表导出

```bash
# 将实验产出的图表直接复制到论文插图目录
cp output/run_xxx/epochs/50/compare.png docs/latex/img/
```

---

*此文件随实验推进持续更新。任何发现的好用技巧、踩坑记录都应补充进来。*

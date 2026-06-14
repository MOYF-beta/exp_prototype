# 使用特定trainer和配置文件启动训练
# 需要按照output中所示的规范输出
# 不要直接调用方法，而是subprocess.run，这样才能正确捕获输出并进行后续处理
# 需要同时把subprocess的stdout和stderr都捕获到，并且输出到控制台同时记录到文件
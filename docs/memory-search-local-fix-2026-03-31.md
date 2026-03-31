# OpenClaw 本地 memory_search 修复记录（2026-03-31）

## 目标

将 OpenClaw 的 `memory_search` 从不可用状态修复为：

- **真正本地运行**
- 不依赖远程 embeddings provider
- 不依赖运行时在线下载模型

最终结果：已完成。

---

## 最终状态

当前 `memory_search` 已恢复为：

- `provider: local`
- `model: /home/lenovo/.openclaw/models/embeddinggemma-300m-qat-Q8_0.gguf`
- `mode: hybrid`

并且实测已经能返回真实记忆结果，例如：

- `MEMORY.md#L1-L15`
- `memory/2026-03-27.md#L1-L11`
- `memory/2026-03-20.md#L7-L10`

---

## 问题现象

最开始看到的是一组容易误导人的表象：

- `make` / `g++` 已安装正常
- QMD 在尝试构建 Vulkan 支持时失败
- 报错里出现：
  - `Could NOT find Vulkan`
  - 缺少 `Vulkan_LIBRARY`、`Vulkan_INCLUDE_DIR`、`glslc`
- 但同时又提示：
  - `falling back to no GPU`
  - `running on CPU`

表面上看像是“Vulkan 问题”，但后续排查发现：

> **Vulkan 不是最终阻塞点，真正阻塞点是本地 embedding 模型的下载链路。**

---

## 排查过程

### 1. 先确认系统依赖

确认：

- `make` 已安装
- `g++` 已安装
- 编译器识别正常

这一步说明基础编译环境不是主因。

---

### 2. 验证 QMD 当前状态

继续检查后发现：

- `qmd` 命令本身可启动
- 但当时 `qmd` 内部并没有有效 collection / embedding 结果
- `memory_search` 返回空，并不代表链路完全正常，只能说明“没有可搜到的向量结果”

之后把 `memory/` 加入 collection，确认文本索引路径基本正常。

---

### 3. 验证 CPU-only 是否成立

为了避免继续被 Vulkan 干扰，尝试了两种方式：

#### 方式 A

```bash
GGML_VULKAN=0 qmd embed
```

结果：

- 仍然会触发 Vulkan 相关前置探测
- 卡在 `Gathering information`

#### 方式 B

```bash
NODE_LLAMA_CPP_GPU=false GGML_VULKAN=0 qmd embed
```

结果：

- 不再继续走 Vulkan 编译探测
- 说明 **`NODE_LLAMA_CPP_GPU=false` 才是更有效的 CPU-only 开关**

但即使如此，流程依然卡住。

---

### 4. 查清真正卡点：不是 CPU 本身，而是模型下载

继续追查进程状态后发现：

- 进程长期停在 `Gathering information`
- `~/.cache/qmd/models/` 仍为空
- 网络连接状态显示到目标地址的 HTTPS 外连停在 `SYN-SENT`

这说明：

> 它并没有进入真正的本地嵌入计算，而是卡在“模型准备/下载”阶段。

---

### 5. 验证网络根因

进一步测试网络连通性：

- `huggingface.co` 能解析 DNS
- `hf-mirror.com` 也能解析 DNS

但 TCP 测试结果是：

- `huggingface.co:443` → **FAIL**
- `hf-mirror.com:443` → **OK**

这一步把根因完全钉死：

> 不是机器没网，而是 **到 HuggingFace 官方站的下载链路不通**。

---

### 6. 为什么没有继续用远程 provider

中途为了验证问题边界，也临时尝试绕开 QMD，回到 OpenClaw 内置 memory 路线。

当时做了：

- 去掉 `memory.backend = "qmd"`
- 让 `memorySearch` 走内置实现
- 保持远程 provider（OpenAI-compatible）配置

结果出现新报错：

- `openai embeddings failed: 503`
- `No available providers`

因此可以确认：

- 远程 embeddings provider 当时也不稳定
- 它只能用于定位问题，不适合作为最终方案

所以最终仍然回到“真本地”目标。

---

## 最终修复方案

### 核心思路

既然：

- OpenClaw 本地模式需要 GGUF embedding 模型
- 自动下载走 HuggingFace 官方链路，而这条链路不通

那么最稳的修法就是：

> **手动从可访问镜像下载模型到本地，再让 OpenClaw 直接使用本地文件。**

---

### 1. 手动下载本地模型

模型：

- `embeddinggemma-300m-qat-Q8_0.gguf`

来源镜像：

- `hf-mirror.com`

下载后保存到：

```text
/home/lenovo/.openclaw/models/embeddinggemma-300m-qat-Q8_0.gguf
```

文件大小约：

- 313 MB

---

### 2. 修改 OpenClaw 配置

修改文件：

```text
~/.openclaw/openclaw.json
```

将 `agents.defaults.memorySearch` 改为：

```json
"memorySearch": {
  "provider": "local",
  "fallback": "none",
  "local": {
    "modelPath": "/home/lenovo/.openclaw/models/embeddinggemma-300m-qat-Q8_0.gguf"
  }
}
```

含义：

- `provider = local`：强制使用本地 embedding
- `fallback = none`：本地失败时不再偷偷退回远程 provider
- `local.modelPath`：直接指向本地 GGUF 文件，避免再次在线下载

---

### 3. 重启 gateway

修改配置后重启 OpenClaw gateway，使新配置生效。

---

### 4. 实测验证

重启后调用 `memory_search`，返回显示：

- `provider: local`
- `model: /home/lenovo/.openclaw/models/embeddinggemma-300m-qat-Q8_0.gguf`
- `mode: hybrid`

并且已经能检索到：

- `MEMORY.md`
- `memory/2026-03-27.md`
- `memory/2026-03-20.md`
- `memory/2026-03-24.md`

这说明：

- 本地模型加载成功
- 本地索引可用
- `memory_search` 功能恢复成功

---

## 关键结论

### 误区

不要把这次问题简单归结为：

- 缺 Vulkan
- 缺 make
- 缺 g++

这些都不是最终根因。

### 真正根因

真正的问题链条是：

1. 本地 memorySearch / QMD 首次需要 embedding 模型
2. 默认会尝试从 HuggingFace 官方站拉取
3. 当前机器到 `huggingface.co:443` 不通
4. 导致模型始终拿不到
5. 所以本地 memorySearch 一直建不起来

### 最稳修法

最稳的方法不是继续纠结 Vulkan，而是：

1. 确认镜像站可通
2. 手动把 GGUF 模型下载到本地
3. `memorySearch.provider = local`
4. 显式写入 `local.modelPath`
5. 禁掉 fallback

---

## 后续建议

### 建议 1：保留本地模型文件

不要删掉：

```text
/home/lenovo/.openclaw/models/embeddinggemma-300m-qat-Q8_0.gguf
```

它已经绕过了首次下载依赖，后续本地 memorySearch 会更稳。

### 建议 2：以后优先显式配置本地路径

如果未来还要迁移或重装，优先用：

- 已下载好的本地 GGUF 文件
- 显式 `local.modelPath`

而不是依赖首次在线拉取。

### 建议 3：如果将来还想继续用 QMD

可以，但要注意：

- QMD 本身不是完全不能用
- 它也会受同样的本地模型准备/下载问题影响
- 所以在这类网络环境下，依然推荐先把模型文件手动准备好

---

## 本次修复的最短结论

一句话总结：

> **不是 Vulkan 修好了，而是我们绕过了 HuggingFace 官方下载阻塞，手动拿到本地 GGUF 模型，再把 OpenClaw 显式切到 local modelPath，最终恢复了真正本地的 memory_search。**

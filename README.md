# ComfyUI-character-selector

## 功能简述

根据预设的角色名称，快速选择对应的 LoRA 模型、正向提示词和负向提示词。

## 角色配置

默认角色库位于 `custom_nodes/ComfyUI-character-selector/characters.json`。

### 自定义角色

为了方便用户添加个人角色数据且不影响插件更新，支持以下自定义方式：

1. **配置文件**：在插件目录下创建 `characters_custom.json`。
2. **数据格式**：参考 `characters.json` 的格式，示例如下：

```json
[
  {
    "name": "角色名",
    "cover": "封面文件名.jpg",
    "positive_prompt": "正向提示词",
    "negative_prompt": "负向提示词",
    "lora1_path": "LoRA 相对路径/文件名",
    "lora1_weight": 0.8,
    "lora1_trigger": "触发词",
    "lora2_path": "",
    "lora2_weight": 0,
    "lora2_trigger": ""
  }
]
```

1. **封面图**：将自定义的预览图放入 `covers_custom/` 文件夹。
2. **持久化**：`characters_custom.json` 和 `covers_custom/` 已被 git 忽略，更新插件不会丢失或冲突。

## 工作流示例

![charactor-selector-example.png](example_workflows%2Fcharactor-selector-example.png)
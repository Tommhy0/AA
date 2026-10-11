# 生成、校验与自动编译

`scripts/aa_tool.py` 只使用 Python 标准库。自动编译由 AzureArchive 的 **AuthoringService / AuthoringCompiler 原生实现**执行，成品为二进制 `.aas`，不是把 JSON 改后缀。

本机验证组合：AzureArchive 1.0 beta（Unity 2023.2.22f1，包含 AzureArchive.Automation API）、BepInEx 6 IL2CPP / .NET 6.0.7。随技能附带 `assets/compiler/AAKit.CompilerBridge.dll` 和源码。其他程序版本须具有同样接口；缺少 BepInEx 或 API 时脚本明确失败，不自动下载或替换程序。

## 命令

下面路径相对技能目录；先定位本技能的绝对目录，再执行。脚本路径和工程路径均加引号。

```powershell
python -B -X utf8 scripts/aa_tool.py discover
python -B -X utf8 scripts/aa_tool.py validate "examples/Schale_Demo.aap2" --require-auto
python -B -X utf8 scripts/aa_tool.py compile "工程.aap2" --require-auto --exe "程序目录/AzureArchive.exe" --data-root "实际数据目录/data"
```

`compile` 默认发布成品到指定数据根的 `saves/<源文件名>.aas` 与 `.build.json`，资源目录为 `saves/<源文件名>/`。程序已有成品会先移到 `data/.aa-kit-backups/<唯一时间目录>/`，发布失败回滚；不通配删除 `.aap`、`.aas.lock` 或其他文件。运行中的播放器可能占用成品，此时发布明确失败，保留原成品和新 build，关闭对应播放后再重试。

- `--no-publish`：只在工程旁的 `.aa-kit-builds/<唯一任务>/build/` 编译，不改当前 saves。
- `--require-auto`：录制准备检查，要求每个选项节点设置有效的 `DefaultOptionId`，缺失时在启动编译器前报错；普通校验仍会警告未设 Auto 的旧工程。选项写法见 [选项与自动录制](project-format.md#选项与自动录制)。
- `--work-dir "目录"`：指定构建/诊断目录；每次使用独立子目录，旧构建不作为本次结果。
- `--name "成品名"`：设置发布文件名，不改变工程内容或 ProjectId。
- `--timeout 90`：限制本次原生子进程等待时间；超时只关闭本次子进程，保留诊断日志。
- `--play`：编译后在一个正常可见的 AzureArchive 窗口请求打开本次 `.aas`，无需编辑模式。返回 `play_requested` 表示程序接受了播放请求，不代表人工看过全部演出。

`discover` 同时列出普通 LocalLow 和实际存在的打包应用根。数据根有歧义时必须明确 `--data-root`。程序位置也可通过 `AZUREARCHIVE_EXE` 或 `--exe` 指定；原机器路径只是候选。不要在其他机器照抄 ASUS 或 Claude 包路径。

## 编译如何运行

首次编译把附带 DLL 放进目标程序的 `BepInEx/plugins/AAKit.CompilerBridge.dll`。已有不同版本先备份；相同版本不重写。组件仅在脚本为自己的子进程设置 `AA_KIT_NATIVE_JOB` 时执行，普通启动不会接管程序。

编译子进程在隐藏的 batchmode/nographics 模式初始化资源，再调用已验证的原生 `compile` 命令：`project`、`out`、`if_version`（源文件 `sha256:`）。组件将原生成功/失败响应写回独立任务目录，并退出。检查进程启动、结构化响应、非空 `.aas`、源文件版本、成品哈希、资源清单和 missing_resources 后，才发布成品。

原技能的 `AzureArchive.exe --cli ...` 曾启动普通资源初始化流程且不返回结果。本次未验证它是可靠入口，不继续沿用。桥接组件直接调用已确认存在的原生接口，不依赖点击 Unity UI，也不依赖右下角 MCP 端口。

如果编译提示缓存/catalog 不可用，先读 [环境说明](environment.md)；不要只改 completeResStructVer。失败时报告原生错误代码、具体字段/节点，以及本次任务目录中的 `player.log`、`request.json.response.json`。不要把静态校验通过当成编译完成。

## 新工程生成

精简输入示例：

```json
{
  "name": "夏莱的午后",
  "title": "夏莱的午后",
  "header": "日常",
  "bg": "BG_MainOffice",
  "bgm": 37,
  "lines": [
    {"text": "阳光落在办公桌上。"},
    {"text": "老师，报告整理好了。", "speaker": 3,
     "stage": [{"slot": 3, "name": "시로코 부상", "faceId": "03"}]}
  ],
  "ending": "今天的工作告一段落。"
}
```

```powershell
python -B -X utf8 scripts/aa_tool.py generate "剧情输入.json" "新工程.aap2"
python -B -X utf8 scripts/aa_tool.py compile "新工程.aap2" --require-auto --exe "程序目录/AzureArchive.exe" --data-root "实际数据目录/data"
```

生成器显式填充背景/BGM、六栏位、节点/行 ID 与默认枚举。背景/BGM 可在某句覆盖并沿用到下一句；stage 必须逐句给出完整在场角色。未写 speaker 为旁白；speaker 为 1..5 时对应 stage 必须有人。自定义角色 name 使用 manifest Identifier。

`generate` 只创建新文件，目标存在时拒绝覆盖，避免重建已有 ID。分支或已有工程直接编辑完整 AAP2，保留已有标识，并用 validate/compile 验收；生成器不擅自压平分支。

## 维护桥接组件

接口版本改变时，在 PowerShell 7 用目标程序自己的 .NET / interop DLL 重新编译：

```powershell
./scripts/build_bridge.ps1 -AppDirectory "程序目录"
```

不需要安装 .NET SDK。源码和随附二进制一并维护；编译失败保留原 DLL。卸载桥接只需关闭脚本启动的实例，然后移走 `BepInEx/plugins/AAKit.CompilerBridge.dll`；保留已生成剧情文件。

## 交付状态

分别报告：静态校验（含所有选项的 Auto 设置）、原生编译、缺失资源/哈希检查、saves 发布、播放请求，以及人工播放验收。录制交付报告所选自动路线；未实际录制不称为录制成功，`playback_reviewed:false` 不能改写为已看完剧情。

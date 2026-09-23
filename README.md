# lakakala/homebrew-tap

lakakala 工具集的 Homebrew tap。

## 使用方法

```
brew tap lakakala/tap
brew trust lakakala/tap   # 较新版本的 Homebrew 需要信任第三方 tap
brew install thther
```

或者一步完成：

```
brew install lakakala/tap/thther
```

## 可用的 formula

| Formula | 说明 |
| ------- | ---- |
| `thther` | 基于 TCP、类似 mosh 的持久化远程终端，支持通过 SSH 引导启动（[仓库](https://github.com/lakakala/thther-tty)） |

## 添加新工具

1. 创建 `Formula/<name>.rb`（可参考 `Formula/thther.rb` 作为模板）：
   - `desc` / `homepage` / `license` —— 取自该工具的仓库。
   - 推荐使用 GitHub Release 中的预编译包（`thther` 即采用此方式）：
     - 用 `on_macos` / `on_linux`（必要时嵌套 `on_arm` / `on_intel`）为每个平台分别写
       `url` 和 `sha256`，`url` 形如
       `https://github.com/lakakala/<repo>/releases/download/v<X.Y.Z>/<name>-v<X.Y.Z>-<target>.tar.gz`。
     - 显式声明 `version "<X.Y.Z>"`。
     - 某平台没有预编译包时用 `depends_on arch: ...` 限制架构（例如 thther 在 macOS 上只支持 arm64）。
     - `install` 中只需 `bin.install "<name>"`。
   - 也可以改为源码编译：`url` 使用某个 tag 的源码 tarball
     `https://github.com/lakakala/<repo>/archive/refs/tags/v<X.Y.Z>.tar.gz`；对于 Rust 工具，只需要
     `depends_on "rust" => :build` 和 `system "cargo", "install", *std_cargo_args`
     （要求工具仓库中已提交 `Cargo.lock`）。
2. 本地验证：先执行 `brew style Formula/<name>.rb`，再执行
   `brew install Formula/<name>.rb` 和 `brew test <name>`。
3. 提交并推送。用户在下次 `brew update` 后即可获取新的 formula。

## 发布工具的新版本

### thther：发布后自动更新

在 `lakakala/thther-tty` 中更新版本号、提交并推送 `v<X.Y.Z>` 标签即可。
上游 Release workflow 等 macOS arm64、Linux arm64 和 Linux x86_64 的构建及上传全部成功后，
向本仓库发送 `thther-release` 事件，载荷为 `{"tag":"v<X.Y.Z>"}`。

本仓库的 **Update thther** workflow 会读取指定的正式 Release，下载三个安装包和对应的
`.sha256` 文件，计算并核对实际摘要。全部通过后才更新 formula，并在 Linux x86_64 上运行
`brew style`、安装和 `brew test`，最后由 `github-actions[bot]` 直接提交到默认分支。
用户执行 `brew update && brew upgrade thther` 即可升级。

- 仅接受 `v<X.Y.Z>` 稳定版；draft 和 prerelease Release 会跳过，旧版本不会覆盖新版本。
- 同版本可以重新校验并修正摘要；没有差异时不会生成提交。
- 附件缺失、下载失败、摘要不符或测试失败时不会推送更新。
- 更新任务串行运行；遇到推送冲突会从最新分支重新生成更新，最多尝试三次，不强制推送。

### 首次启用

1. 将本仓库的 workflow、脚本和测试提交到默认分支（当前为 `main`），并启用 GitHub Actions。
   `repository_dispatch` 接收 workflow 必须已经存在于默认分支。
2. 创建一个 fine-grained PAT，资源所有者选择 `lakakala`，仓库仅选择 `homebrew-tap`，
   Repository permissions 中授予 **Contents: Read and write**。
   在 **thther-tty 仓库**的 Settings → Secrets and variables → Actions 中添加
   `HOMEBREW_TAP_TOKEN`，值为该 PAT；不要将凭据写入仓库。到期前更新此 Secret。
3. 将上游 Release workflow 的 `notify-homebrew` 任务提交到 `thther-tty`。
   上游内置 `GITHUB_TOKEN` 无法替代跨仓库凭据；通知任务缺少 Secret 或请求失败时会报错，
   已上传的 Release 附件仍然保留。
4. 本仓库使用自身 `GITHUB_TOKEN` 的 `contents: write` 权限提交更新。
   仓库 Actions 策略及默认分支规则必须允许该机器人直接推送。
5. 在本仓库 Actions → **Update thther** → **Run workflow** 中选择默认分支，
   输入 `v0.1.3` 验证，再运行一次确认没有重复提交。

配置参考：[GitHub repository_dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#repository_dispatch)、
[跨仓库事件权限](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)。

### 补跑和本地验证

通知失败时可在上游重跑失败的 `Update Homebrew tap` 任务；tap 更新失败时可重跑本仓库的
workflow，或通过 **Run workflow** 手动输入已发布的稳定版标签。
查看两个仓库的 Actions 日志定位失败步骤；修复缺失附件或权限后再补跑。

脚本仅依赖 Python 3.9+ 标准库；`GH_TOKEN` 可选，用于提高 GitHub API 请求限额。

```sh
# 下载并验证真实安装包，只展示差异，不修改 formula
python3 scripts/update_thther.py --tag v0.1.3 --dry-run

# 使用离线 Release fixtures 测试更新及失败行为
python3 -m unittest discover -s tests -v

# 手动更新本地 formula（不提交、不推送）
python3 scripts/update_thther.py --tag v0.1.3
brew style Formula/thther.rb
```

### 其他工具：手动更新

1. 在工具仓库中更新版本号，提交并推送 `v<X.Y.Z>` 标签，等待 Release 附件上传完毕。
2. 获取每个平台包的校验和，读取对应 `.sha256` 附件，或者：

   ```
   curl -L https://github.com/lakakala/<repo>/releases/download/v<X.Y.Z>/<name>-v<X.Y.Z>-<target>.tar.gz | sha256sum
   ```

3. 更新 `Formula/<name>.rb` 中的 `version`、各平台的 `url` 和 `sha256`，验证后提交并推送。

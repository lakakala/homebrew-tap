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

1. 在工具仓库中：更新版本号，提交，打上 `v<X.Y.Z>` 标签并推送，等待 CI 把各平台的包上传到 GitHub Release。
2. 获取每个平台包的校验和：直接读取 Release 中对应的 `.sha256` 附件，或者

   ```
   curl -L https://github.com/lakakala/<repo>/releases/download/v<X.Y.Z>/<name>-v<X.Y.Z>-<target>.tar.gz | sha256sum
   ```

3. 更新 `Formula/<name>.rb` 中的 `version` 以及每个平台的 `url` 和 `sha256`，提交并推送。

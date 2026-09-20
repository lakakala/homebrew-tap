# lakakala/homebrew-tap

Homebrew tap for lakakala's tools.

## Usage

```
brew tap lakakala/tap
brew trust lakakala/tap   # newer Homebrew requires trusting third-party taps
brew install thther
```

or in one step:

```
brew install lakakala/tap/thther
```

## Available formulae

| Formula | Description |
| ------- | ----------- |
| `thther` | TCP-based mosh-like persistent remote terminal with SSH bootstrap ([repo](https://github.com/lakakala/thther-tty)) |

## Adding a new tool

1. Create `Formula/<name>.rb` (use `Formula/thther.rb` as a template):
   - `desc` / `homepage` / `license` — from the tool's repo.
   - `url` — the GitHub source tarball of a tag:
     `https://github.com/lakakala/<repo>/archive/refs/tags/v<X.Y.Z>.tar.gz`
   - `sha256` — checksum of that tarball (see below).
   - For Rust tools, `depends_on "rust" => :build` and
     `system "cargo", "install", *std_cargo_args` are all you need
     (requires a committed `Cargo.lock` in the tool's repo).
2. Verify locally: `brew style Formula/<name>.rb`, then
   `brew install --build-from-source Formula/<name>.rb` and `brew test <name>`.
3. Commit and push. Users get the new formula on their next `brew update`.

## Releasing a new version of a tool

1. In the tool's repo: bump the version, commit, tag `v<X.Y.Z>`, push the tag.
2. Compute the tarball checksum (must be GitHub's tarball, not a local archive):

   ```
   curl -L https://github.com/lakakala/<repo>/archive/refs/tags/v<X.Y.Z>.tar.gz | sha256sum
   ```

3. Update `url` and `sha256` in `Formula/<name>.rb`, commit, push.

class Thther < Formula
  desc "TCP-based mosh-like persistent remote terminal with SSH bootstrap"
  homepage "https://github.com/lakakala/thther-tty"
  version "0.1.1"
  license "MIT"

  on_macos do
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.1/thther-v0.1.1-aarch64-apple-darwin.tar.gz"
      sha256 "c17fcc55f42f89b1ceea98919eba4f61af76e4792bd582f8cc6be656c0b9808d"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.1/thther-v0.1.1-aarch64-unknown-linux-gnu.tar.gz"
      sha256 "165ddae544f44ade6f1db4a1f2489765aee4f5c5cb8283e372ac8d11bb7ca7b6"
    end
    on_intel do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.1/thther-v0.1.1-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "82122b0f7cce7797368aeab0731be7feae18a1d7a679e5a717b3e14b23a8f3e6"
    end
  end

  def install
    bin.install "thther"
  end

  test do
    assert_match "thther #{version}", shell_output("#{bin}/thther --version")
  end
end

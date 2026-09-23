class Thther < Formula
  desc "TCP-based mosh-like persistent remote terminal with SSH bootstrap"
  homepage "https://github.com/lakakala/thther-tty"
  version "0.1.2"
  license "MIT"

  on_macos do
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.2/thther-v0.1.2-aarch64-apple-darwin.tar.gz"
      sha256 "470c614718a3631b87c716b9548c5f1784f1e72a0d521b9be3b1ca1b6288db65"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.2/thther-v0.1.2-aarch64-unknown-linux-gnu.tar.gz"
      sha256 "ee6c055f6601bb30089125d421abfdd536691a1af970fa3b7ac116670f0ae083"
    end
    on_intel do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.2/thther-v0.1.2-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "5ce50a7709c72c1ba9fb27fb665cdbc1b6161e135d2f5d922c8036b77df9dbce"
    end
  end

  def install
    bin.install "thther"
  end

  test do
    assert_match "thther #{version}", shell_output("#{bin}/thther --version")
  end
end

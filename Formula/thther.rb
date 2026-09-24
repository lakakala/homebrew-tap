class Thther < Formula
  desc "TCP-based mosh-like persistent remote terminal with SSH bootstrap"
  homepage "https://github.com/lakakala/thther-tty"
  version "0.1.6"
  license "MIT"

  on_macos do
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.6/thther-v0.1.6-aarch64-apple-darwin.tar.gz"
      sha256 "9b21cd858b3d84ef5a2a48a566dc04de9fe06133362387e36a3a2a12d800d42f"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.6/thther-v0.1.6-aarch64-unknown-linux-gnu.tar.gz"
      sha256 "9f09bfb4d1fca4dbde8a2fb0c58d9a4e52c3f1643026ceb28243bb6d2fc54446"
    end
    on_intel do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.6/thther-v0.1.6-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "23ecbc983277c3d11a10c65109ef8f5267bf215427131035a773a279f21a61de"
    end
  end

  def install
    bin.install "thther"
  end

  test do
    assert_match "thther #{version}", shell_output("#{bin}/thther --version")
  end
end

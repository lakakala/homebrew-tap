class Thther < Formula
  desc "TCP-based mosh-like persistent remote terminal with SSH bootstrap"
  homepage "https://github.com/lakakala/thther-tty"
  version "0.1.4"
  license "MIT"

  on_macos do
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.4/thther-v0.1.4-aarch64-apple-darwin.tar.gz"
      sha256 "715993e5c5edfecabebd5ae3d87c5806b81e06b73271dd9d0c119dc86fa1ad80"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.4/thther-v0.1.4-aarch64-unknown-linux-gnu.tar.gz"
      sha256 "72250b7a55d49561615d6cf8ff180b4175047f2833b422ec882b9e45d836dc9e"
    end
    on_intel do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.4/thther-v0.1.4-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "09d7d7132f6b286087a56747d7773e0aa9d9568ecfd321b967ff8fbaf000f2d7"
    end
  end

  def install
    bin.install "thther"
  end

  test do
    assert_match "thther #{version}", shell_output("#{bin}/thther --version")
  end
end

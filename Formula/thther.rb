class Thther < Formula
  desc "TCP-based mosh-like persistent remote terminal with SSH bootstrap"
  homepage "https://github.com/lakakala/thther-tty"
  version "0.1.3"
  license "MIT"

  on_macos do
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.3/thther-v0.1.3-aarch64-apple-darwin.tar.gz"
      sha256 "edc96d5e7e4d1354ab0da28c4ba6adbb0e8a77fc26ca07b54064eea12d6350d4"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.3/thther-v0.1.3-aarch64-unknown-linux-gnu.tar.gz"
      sha256 "d7a638a5335942f091dc6ace35bfbd72799411b29931af3f9227d5d93ffbb5fa"
    end
    on_intel do
      url "https://github.com/lakakala/thther-tty/releases/download/v0.1.3/thther-v0.1.3-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "f5edf39f2b860351dd888bd692807203639ed228699660b8c0ba2b5089f7a242"
    end
  end

  def install
    bin.install "thther"
  end

  test do
    assert_match "thther #{version}", shell_output("#{bin}/thther --version")
  end
end

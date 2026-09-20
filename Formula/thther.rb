class Thther < Formula
  desc "TCP-based mosh-like persistent remote terminal with SSH bootstrap"
  homepage "https://github.com/lakakala/thther-tty"
  url "https://github.com/lakakala/thther-tty/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # TODO: fill in after tagging v0.1.0
  license "MIT"
  head "https://github.com/lakakala/thther-tty.git", branch: "main"

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args
  end

  test do
    assert_match "thther #{version}", shell_output("#{bin}/thther --version")
  end
end

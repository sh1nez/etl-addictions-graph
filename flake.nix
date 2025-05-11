{
  description = "Dev environment for etl-addictions-graph with Python dependencies";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }: let
    inherit (nixpkgs) lib;
    pkgs_x86 = nixpkgs.legacyPackages.x86_64-darwin;
    pkgs_arm = nixpkgs.legacyPackages.aarch64-darwin;
    makeShell = pkgset: pkgset.mkShell;
  in {
    devShells.x86_64-darwin.default = makeShell pkgs_x86 {
      buildInputs = [
        (pkgs_x86.python312.withPackages (ps: with ps; [
          matplotlib
          networkx
          pyqt6
          sqlglot
          black
          coverage
          pytest
        ]))
        pkgs_x86.pre-commit
      ];
      nativeBuildInputs = [
        pkgs_x86.zlib
        pkgs_x86.libjpeg
        pkgs_x86.libtiff
        pkgs_x86.lcms2
        pkgs_x86.git
      ];
      shellHook = ''echo "Dev shell (x86_64) ready for Python 3.12"'';
    };

    devShells.aarch64-darwin.default = makeShell pkgs_arm {
      buildInputs = [
        (pkgs_arm.python312.withPackages (ps: with ps; [
          matplotlib
          networkx
          pyqt6
          sqlglot
          black
          coverage
          pytest
        ]))
        pkgs_arm.pre-commit
      ];
      nativeBuildInputs = [
        pkgs_arm.zlib
        pkgs_arm.libjpeg
        pkgs_arm.libtiff
        pkgs_arm.lcms2
        pkgs_arm.git
      ];
      shellHook = ''echo "Dev shell (aarch64) ready for Python 3.12"'';
    };
  };
}


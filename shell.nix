{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python313
    pkgs.python313Packages.pip
    pkgs.python313Packages.setuptools
    pkgs.python313Packages.wheel
    pkgs.libjpeg
    pkgs.zlib
    pkgs.git
    pkgs.libtiff
    pkgs.lcms2
  ];

  shellHook = ''
    export CFLAGS="-I${pkgs.libjpeg.dev}/include -I${pkgs.zlib.dev}/include"
    export LDFLAGS="-L${pkgs.libjpeg.out}/lib -L${pkgs.zlib.out}/lib"
    echo "JPEG headers in ${pkgs.libjpeg.dev}/include"
  '';
}


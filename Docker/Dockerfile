FROM nixos/nix:latest

COPY . /app
WORKDIR /app

RUN NIX_PATH=nixpkgs=channel:nixos-unstable nix-shell -p python3 python3Packages.yapf --run "./scripts/yapf.sh"

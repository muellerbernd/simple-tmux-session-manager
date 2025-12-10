{
  description = "Python devShell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = [ ];
        pkgs = import nixpkgs { inherit system overlays; };
      in
      with pkgs;
      {
        # Rust package
        devShells.default = mkShell {
          name = "devShell";

          buildInputs = [
            python3
          ];

          shellHook = "";
        };
      }
    );
}

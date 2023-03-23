{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.05";
    pypi-deps-db = {
      url = "github:DavHau/pypi-deps-db";
      flake = false;
    };
    mach-nix = {
      url = "github:DavHau/mach-nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
      inputs.pypi-deps-db.follows = "pypi-deps-db";
    };
  };

  outputs = { self, nixpkgs, flake-utils, mach-nix, ... }: # , mach-nix, pypi-deps-db
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pypkgs = pkgs.python310Packages;

        machPythonEnv = mach-nix.lib."${system}".mkPython {
          ignoreDataOutdated = true;
          python = "python310";
          requirements = ''
            requests
            pyyaml
            drawsvg
            click
            islenska
            setuptools
          '';
        };

        project-deps = with pkgs; [
          stdenv
          machPythonEnv
        ];

        project-env = pkgs.buildEnv {
          name = "project-env";
          paths = project-deps;
        };

        script_header = ''
          #!${pkgs.stdenv.shell}
        '';

        script_content = {
          run = ''
            ${project-env}/bin/python -m gentool $@
          '';
        };

        scripts = builtins.mapAttrs
          (name: value: flake-utils.lib.mkApp {
            drv = pkgs.writeScriptBin "${name}" ''
              ${script_header}
              ${value}
            '';
          })
          script_content;
      in
      rec
      {
        apps = scripts // {
          default = scripts.run;
        };

        devShell = pkgs.mkShell {
          packages = project-deps;
        };
      });
}

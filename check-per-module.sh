#!/usr/bin/env bash

# check-perl-module: Check if a Perl module is installed, print its version,
# and optionally its installation path (via perldoc).

# Exit codes:
# 0 module is installed
# 1 module is not installed
# 2 usage error
# 3 perl not found

# Usage:
# check-perl-module Module::Name
# check-perl-module -p Module::Name     # also print path

set -euo pipefail

show_usage() {
  cat >&2 <<'USAGE'
Usage:
  check-perl-module Module::Name
  check-perl-module -p Module::Name   # also print module path

Description:
  Loads the module using `require` (does NOT call import), prints its version
  if available (or "unknown"), and exits 0 if installed, 1 if not installed.

Options:
  -p   Also print the module's installation path (uses `perldoc -l` if available).
  -h   Show this help.

Exit codes:
  0  installed
  1  not installed
  2  usage error
  3  perl not found
  USAGE
}

parse_args(){
  if [[ $# -eq 0 ]]; then
    show_usage
    exit 2
  fi

  while [[ $# -gt 0 ]]; do
    case "${1}" in
      -h|--help)
        show_usage
        exit 0
        ;;
      -p|--path)
        print_path=true
        shift
        ;;
      -*)
        echo "Unknown option: ${1}" >&2
        show_usage
        exit 2
        ;;
      *)
        module="${1}"
        shift
        ;;
    esac
  done
}

print_path=false
module=""

parse_args "$@"

if [[ -z "${module:-}" ]]; then
  show_usage
  exit 2
fi

# Ensure perl exists
if ! command -v perl >/dev/null 2>&1; then
  echo "perl not found in PATH" >&2
  exit 3
fi

# Check installation and print version (without calling import)
version_output="$(perl -Mstrict -Mwarnings -e '
  my $module = shift;

  # Try to require the module WITHOUT calling import (avoids needing args)
  my $ok = eval "require $module";
  if (!$ok) {
    print qq(NOT INSTALLED\n);
    exit 1;
  }

  # Try ->VERSION (safe), fall back to $Package::VERSION
  my $version = eval { $module->VERSION } // do {
    no strict "refs";
    ${"${module}::VERSION"};
  };

  print((defined $version ? $version : "unknown"), "\n");
  exit 0;
' "${module}" 2>&1)" || {
  echo "${version_output}"
  exit 1
}

# If we reach here, module is installed. Print the version.
echo "${version_output}"

# Optionally print path (best-effort)
if "${print_path}"; then
  if command -v perldoc >/dev/null 2>&1; then
    path="$(perldoc -l "${module}" 2>/dev/null || true)"
    if [[ -n "${path}" ]]; then
      echo "path: ${path}"
    else
      echo "path: unknown"
    fi
  else
    echo "path: perldoc not found"
  fi
fi

#!/usr/bin/env bash
set -euo pipefail

show_usage() {
  cat >&2 <<'USAGE'
Usage:
  check-perl-module Module::Name
  check-perl-module -p Module::Name   # also print module path
  check-perl-module -E Module::Name   # on failure, show full Perl load error

Description:
  Check if a Perl module is installed, print its version, and optionally its installation path (via perldoc).

Options:
  -p, --path        Also print the module's installation path (uses `perldoc -l` if available).
  -E, --show-error  When module fails to load, print Perl's full error.
  -h, --help        Show this help.

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
      -E|--show-error)
        show_error=1
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

# Try to require the module WITHOUT calling import (avoids needing args)
# If module can be required, try to print the version
check_installed(){
  local module="$1"
  local show="$2" # "1" to show error details, "0" otherwise

  if [[ -z "$module" ]]; then
    echo "Error: module name required" >&2
    exit 2
  fi

  perl -e '
    my ($m, $show) = @ARGV;

    # Try to require the module and capture full error on failure
    eval { require $m; 1 }
      or do {
        print $@ if ($show);
        exit 1;
      };

    # If we got here, the module loaded; try to get version
    my $version = eval { $m->VERSION } // do {
      no strict "refs";
      ${"${m}::VERSION"};
    };

    print((defined $version ? $version : "version not available"), "\n");
    exit 0
  ' "$module" "$show"
}

print_path=false
show_error=0
module=""

parse_args "$@"

# Check that a module was provided
if [[ -z "${module:-}" ]]; then
  show_usage
  exit 2
fi

# Ensure perl exists
if ! command -v perl >/dev/null 2>&1; then
  echo "perl not found in PATH" >&2
  exit 3
fi

# Require Perl exactly 5.42.0
if ! perl -e 'exit(($^V eq v5.42.0) ? 0 : 1)'; then
  echo "Error: This script requires Perl 5.42.0 exactly." >&2
  perl -e 'print "Found Perl version: ", $^V, "\n"'
  exit 3
fi

# Check installation and print version
if check_installed "$module" "$show_error"; then
  echo "Installed"
else
  if [[ "$show_error" -eq 1 ]]; then
    exit 1
  else  
    echo "Not installed"
    exit 1
  fi
fi

# Optionally print path (best-effort)
if [[ "${print_path}" == true ]]; then
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

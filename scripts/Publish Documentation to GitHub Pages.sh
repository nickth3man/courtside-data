#!/bin/bash

function main() {
  local -r uv_program_path="$1"
  if [[ ! -e "${uv_program_path}" ]]; then printf "Cannot execute uv at ${uv_program_path}\n" && exit 255; fi

  "${uv_program_path}" run -- mkdocs gh-deploy --clean --force
  local uv_exit_code="$?"
  if [[ "0" != "${uv_exit_code}" ]]; then printf "Cannot run mkdocs using uv program at ${uv_program_path}\n" && exit 255; fi
}

main "$@"

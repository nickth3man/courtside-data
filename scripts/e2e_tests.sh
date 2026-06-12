#!/bin/bash

# TODO: @jaebradley move the duplicative script setup into it's own helper script

function main() {
  local -r dependencies_folder_path="$1"
  mkdir -p "${dependencies_folder_path}"
  if [[ "0" != "$?" ]]; then printf "Creating dependencies folder at ${dependencies_folder_path} failed\n" && exit 255; fi

  command -v "python3"
  if [[ "0" != "$?" ]]; then printf "Cannot identify python3 program\n" && exit 255; fi

  python3 -m venv "${dependencies_folder_path}"
  if [[ "0" != "$?" ]]; then printf "Cannot create python3 virtual environment in ${dependencies_folder_path}\n" && exit 255; fi

  local -r pip_program_path="${dependencies_folder_path}/bin/pip3"
  "${pip_program_path}" install -U pip setuptools
  if [[ "0" != "$?" ]]; then printf "Cannot execute pip program at ${pip_program_path}\n" && exit 255; fi

  "${pip_program_path}" install uv
  if [[ "0" != "$?" ]]; then printf "Cannot install uv at ${pip_program_path}\n" && exit 255; fi

  local -r uv_program_path="${dependencies_folder_path}/bin/uv"
  "${uv_program_path}" sync --extra dev --frozen
  if [[ "0" != "$?" ]]; then printf "Cannot execute uv sync at ${uv_program_path}\n" && exit 255; fi

  "${uv_program_path}" run coverage run --source=courtside_data --module pytest \
    --ignore="tests/integration/" \
    --ignore="tests/unit/"

  local uv_exit_code="$?"
  # https://docs.pytest.org/en/7.1.x/reference/exit-codes.html#:~:text=Exit%20code%205,No%20tests%20were%20collected&text=If%20you%20would%20like%20to,using%20the%20pytest%2Dcustom_exit_code%20plugin.
  if [[ "5" == "${uv_exit_code}" ]]; then printf "pytest using uv program at ${uv_program_path} did not collect any tests" && exit 0; fi
  if [[ "0" != "${uv_exit_code}" ]]; then printf "Cannot run pytest using uv program at ${uv_program_path}\n" && exit 255; fi
}

main "$@"

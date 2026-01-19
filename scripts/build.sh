#!/bin/bash

function main() {
  local -r dependencies_folder_path="$1"
  mkdir -p "${dependencies_folder_path}"
  if [[ "0" != "$?" ]]; then printf "Creating dependencies folder at ${dependencies_folder_path} failed\n" && exit 255; fi

  uv sync
  if [[ "0" != "$?" ]]; then printf "Cannot execute uv sync\n" && exit 255; fi

  # Intentionally ignore end to end tests as they execute HTTP requests to basketball reference.com and are subject to
  # rate limits
  uv run coverage run --source=basketball_reference_web_scraper --module pytest \
    --ignore="tests/end to end/"

  local uv_exit_code="$?"
  # https://docs.pytest.org/en/7.1.x/reference/exit-codes.html#:~:text=Exit%20code%205,No%20tests%20were%20collected&text=If%20you%20would%20like%20to,using%20the%20pytest%2Dcustom_exit_code%20plugin.
  if [[ "5" == "${uv_exit_code}" ]]; then printf "pytest using uv did not collect any tests" && exit 0; fi
  if [[ "0" != "${uv_exit_code}" ]]; then printf "Cannot run pytest using uv\n" && exit 255; fi

  uv run coverage xml
  if [[ "0" != "$?" ]]; then printf "Cannot run coverage xml using uv\n" && exit 255; fi
}

main "$@"

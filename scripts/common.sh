#!/bin/bash
# Common functions for build scripts

# Create dependencies folder and sync with uv
setup_dependencies() {
    local -r dependencies_folder_path="$1"
    mkdir -p "${dependencies_folder_path}"
    if [[ "0" != "$?" ]]; then
        printf "Creating dependencies folder at ${dependencies_folder_path} failed\n"
        exit 255
    fi

    uv sync
    if [[ "0" != "$?" ]]; then
        printf "Cannot execute uv sync\n"
        exit 255
    fi
}

# Run pytest with coverage and handle exit codes
run_pytest_with_coverage() {
    local -r pytest_ignore_args="$1"

    uv run coverage run --module pytest ${pytest_ignore_args}

    local uv_exit_code="$?"
    # https://docs.pytest.org/en/7.1.x/reference/exit-codes.html
    if [[ "5" == "${uv_exit_code}" ]]; then
        printf "pytest did not collect any tests\n"
        exit 0
    fi
    if [[ "0" != "${uv_exit_code}" ]]; then
        printf "Cannot run pytest\n"
        exit 255
    fi
}

# Check coverage meets minimum threshold
check_coverage_threshold() {
    uv run coverage report --fail-under=90
    if [[ "0" != "$?" ]]; then
        printf "Coverage is below 90% threshold\n"
        exit 255
    fi
}

# Generate coverage XML report
generate_coverage_xml() {
    uv run coverage xml
    if [[ "0" != "$?" ]]; then
        printf "Cannot generate coverage XML\n"
        exit 255
    fi
}
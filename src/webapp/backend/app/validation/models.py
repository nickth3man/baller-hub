"""Validation models for database data quality checks."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON as JSONType
from sqlmodel import Field as SQLField, SQLModel


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class Category(str, Enum):
    REFERENTIAL_INTEGRITY = "REFERENTIAL_INTEGRITY"
    DATA_CONSISTENCY = "DATA_CONSISTENCY"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    DATA_QUALITY = "DATA_QUALITY"


class ValidationIssue(BaseModel):
    """Single validation violation."""

    rule_id: str = Field(description="Unique identifier for the validation rule")
    rule_name: str = Field(description="Human-readable rule name")
    severity: Severity = Field(description="Impact level")
    category: Category = Field(description="Validation category")
    table_name: str = Field(description="Affected table")
    row_identifier: Any | None = Field(
        default=None, description="Primary key of affected row"
    )

    error_type: str = Field(description="Type of validation error")
    error_message: str = Field(description="Human-readable error description")
    expected_value: str | None = Field(default=None, description="Expected value")
    actual_value: str | None = Field(default=None, description="Actual value received")

    sample_rows: list[dict] = Field(
        default_factory=list, description="Example violating rows"
    )
    affected_count: int = Field(default=0, description="Total affected rows")

    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "GAME_TEAMS_DIFFERENT",
                "rule_name": "Home and away teams must be different",
                "severity": "CRITICAL",
                "category": "BUSINESS_LOGIC",
                "table_name": "game",
                "row_identifier": 12345,
                "error_type": "business_rule_violation",
                "error_message": "Home team cannot be same as away team",
                "expected_value": "Different team IDs",
                "actual_value": "home_team_id = away_team_id",
                "sample_rows": [{"game_id": 12345}],
                "affected_count": 1,
            }
        }


class ValidationSummary(BaseModel):
    """Summary statistics for a validation run."""

    total_rules: int = Field(description="Total validation rules run")
    rules_passed: int = Field(description="Number of rules that passed")
    rules_failed: int = Field(description="Number of rules that failed")
    critical_issues: int = Field(description="Number of critical issues")
    major_issues: int = Field(description="Number of major issues")
    minor_issues: int = Field(description="Number of minor issues")

    total_rows_checked: int = Field(default=0, description="Total rows validated")
    total_affected_rows: int = Field(default=0, description="Total rows with issues")

    success_rate: float = Field(description="Percentage of rules that passed")

    duration_seconds: float = Field(description="Validation run duration in seconds")


class ValidationResult(BaseModel):
    """Complete validation run result."""

    run_id: str = Field(description="Unique run identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    target_tables: list[str] = Field(description="Tables that were validated")
    filter_rules: list[str] | None = Field(
        default=None, description="Rules that were filtered"
    )

    summary: ValidationSummary = Field(description="Summary of validation results")
    issues: list[ValidationIssue] = Field(
        default_factory=list, description="All issues found"
    )

    config_version: str = Field(default="1.0", description="Validation config version")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ValidationRun(SQLModel, table=True):
    """Database model for storing validation runs."""

    __tablename__ = "validation_run"

    run_id: str = SQLField(primary_key=True, max_length=50)
    timestamp: datetime = SQLField(default_factory=datetime.utcnow, index=True)

    target_tables: list[str] | None = SQLField(default=None, sa_type=JSONType)

    summary: dict[str, Any] | None = SQLField(default=None, sa_type=JSONType)

    issues: list[dict[str, Any]] | None = SQLField(default=None, sa_type=JSONType)

    duration_seconds: float = SQLField(default=0.0)

    triggered_by: str = SQLField(default="manual", max_length=50)
    git_commit: str | None = SQLField(default=None, max_length=50)

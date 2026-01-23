# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Context:** SQLModel Database Definition

## OVERVIEW
This directory contains the SQLModel definitions that serve as both SQLAlchemy database tables and Pydantic data models. These models define the schema for the application's persistent data.

## FOLDER STRUCTURE
- `__init__.py`: Exports all models for easy access.
- `*.py`: Individual model definitions (e.g., `player.py`, `team.py`).

## CORE BEHAVIORS & PATTERNS
- **Flat Inheritance**: Models inherit directly from `SQLModel` (or a base table=True class).
- **Primary Keys**: Use `{model}_id` naming convention (e.g., `player_id`, not `id`).
- **Enums**: Use `SAEnum` (SQLAlchemy Enum) for categorical fields.
- **JSON Fields**: Use `pydantic.Json` or SQLAlchemy `JSON` types for unstructured data.
- **Strict Relationships**: Define explicit `Relationship` attributes with back_populates.

## CONVENTIONS
- **No Mixins**: Avoid complex mixin inheritance; prefer explicit field definitions.
- **Table Names**: Snake_case table names (usually matching the class name converted).
- **Foreign Keys**: Explicitly define foreign key fields and relationship attributes.
- **Type Hints**: Use `Optional[T]` for nullable fields.

## WORKING AGREEMENTS
- **Migrations**: Changes here require an Alembic migration generation.
- **Validation**: Ensure Pydantic validation rules are logical at the model level.
- **Circular Imports**: Use `TYPE_CHECKING` blocks for relationship type hints to avoid cycles.

#!/usr/bin/env python3
"""
CSV Relationship Analyzer for NBA Data

This script analyzes the inter and intra relationships between all CSV files
in the raw-data/csv directory. It identifies:
- Column schemas and data types
- Potential primary keys and foreign key relationships
- Data quality metrics (nulls, duplicates, cardinality)
- Cross-file relationships based on column name matching and value overlap
- Intra-file relationships (column correlations)

Usage:
    python analyze_csv_relationships.py [--csv-dir PATH] [--output-dir PATH] [--sample-size N]
"""

import argparse
import json
import sys
import warnings
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


class CSVRelationshipAnalyzer:
    """
    Analyzes relationships between and within CSV files.

    Attributes:
        csv_dir (Path): Path to directory containing CSV files.
        sample_size (int): Number of rows to sample for large files.
        file_schemas (dict): Dictionary mapping filenames to their analyzed schemas.
        dataframes (dict): Dictionary mapping filenames to sampled pandas DataFrames.
        relationships (list): List of discovered inter-file relationships.
        intra_relationships (dict): Dictionary mapping filenames to intra-file relationships.
    """

    # Known ID column patterns for relationship detection
    ID_PATTERNS: ClassVar[list[str]] = [
        "id",
        "_id",
        "Id",
        "ID",
        "person_id",
        "personId",
        "player_id",
        "playerId",
        "team_id",
        "teamId",
        "teamid",
        "game_id",
        "gameId",
        "gameid",
        "season",
        "season_id",
        "official_id",
        "draft_type",
    ]

    # Known relationship columns (same concept, different names)
    COLUMN_ALIASES: ClassVar[dict[str, list[str]]] = {
        "player_id": ["personId", "person_id", "player_id", "playerId", "id"],
        "team_id": [
            "teamId",
            "team_id",
            "teamid",
            "hometeamId",
            "awayteamId",
            "team_id_home",
            "team_id_away",
            "opponentTeamId",
            "visitor_team_id",
            "home_team_id",
        ],
        "game_id": ["gameId", "game_id", "gameid"],
        "season": ["season", "season_id", "seasonYear", "season_year"],
        "team_name": [
            "team",
            "teamName",
            "team_name",
            "hometeamName",
            "awayteamName",
            "team_name_home",
            "team_name_away",
            "full_name",
            "nickname",
        ],
        "team_abbrev": [
            "abbreviation",
            "team_abbreviation",
            "teamAbbrev",
            "tm",
            "team_abbreviation_home",
            "team_abbreviation_away",
        ],
        "player_name": [
            "player",
            "player_name",
            "full_name",
            "display_first_last",
            "firstName",
            "first_name",
            "lastName",
            "last_name",
        ],
    }

    def __init__(self, csv_dir: str, sample_size: int = 10000):
        """
        Initialize the analyzer.

        Args:
            csv_dir: Path to directory containing CSV files
            sample_size: Number of rows to sample for large files
        """
        self.csv_dir = Path(csv_dir)
        self.sample_size = sample_size
        self.file_schemas: dict[str, dict] = {}
        self.dataframes: dict[str, pd.DataFrame] = {}
        self.relationships: list[dict] = []
        self.intra_relationships: dict[str, list[dict]] = {}

    def discover_files(self) -> list[Path]:
        """
        Find all CSV files in the directory.

        Returns:
            list[Path]: List of Paths to discovered CSV files.
        """
        return sorted(self.csv_dir.glob("*.csv"))

    def load_csv(self, filepath: Path) -> pd.DataFrame | None:
        """
        Load a CSV file with appropriate encoding handling.

        Args:
            filepath (Path): Path to the CSV file to load.

        Returns:
            pd.DataFrame | None: The loaded DataFrame, or None if loading failed.
        """
        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                return pd.read_csv(
                    filepath, encoding=encoding, low_memory=False, on_bad_lines="skip"
                )
            except Exception:
                continue

        print(f"  Warning: Could not load {filepath.name}")
        return None

    def analyze_column(self, series: pd.Series, col_name: str) -> dict:
        """
        Analyze a single column for its characteristics.

        Args:
            series (pd.Series): The column data to analyze.
            col_name (str): The name of the column.

        Returns:
            dict: Analysis results including type, null count, and uniqueness.
        """
        total = len(series)

        non_null = series.notna().sum()
        null_count = total - non_null

        # Get unique values (sample if too large)
        try:
            unique_count = series.nunique(dropna=True)
        except Exception:
            unique_count = -1

        # Determine data type
        inferred_type = str(series.dtype)
        if series.dtype == "object":
            # Check if it could be numeric
            sample = series.dropna().head(100)
            try:
                pd.to_numeric(sample)
                inferred_type = "numeric_string"
            except Exception:
                # Check if datetime
                try:
                    pd.to_datetime(sample)
                    inferred_type = "datetime_string"
                except Exception:
                    inferred_type = "string"

        # Check if potential ID column
        is_potential_id = (unique_count == total and null_count == 0) or any(
            pattern.lower() in col_name.lower() for pattern in self.ID_PATTERNS
        )

        # Get sample values
        sample_values = series.dropna().head(5).tolist()

        return {
            "column_name": col_name,
            "dtype": inferred_type,
            "total_rows": total,
            "non_null_count": int(non_null),
            "null_count": int(null_count),
            "null_percent": round(null_count / total * 100, 2) if total > 0 else 0,
            "unique_count": int(unique_count),
            "cardinality_ratio": round(unique_count / non_null, 4)
            if non_null > 0
            else 0,
            "is_potential_id": is_potential_id,
            "sample_values": [str(v)[:100] for v in sample_values[:5]],
        }

    def analyze_file_schema(self, filepath: Path) -> dict | None:
        """
        Analyze the schema and characteristics of a single CSV file.

        Args:
            filepath (Path): Path to the CSV file to analyze.

        Returns:
            dict | None: The analyzed schema, or None if the file could not be loaded.
        """
        print(f"  Analyzing: {filepath.name}")

        df = self.load_csv(filepath)
        if df is None:
            return None

        # Sample large files
        if len(df) > self.sample_size:
            df_sample = df.sample(n=self.sample_size, random_state=42)
            sampled = True
        else:
            df_sample = df
            sampled = False

        # Store dataframe for relationship analysis
        self.dataframes[filepath.name] = df_sample

        # Analyze each column
        columns = []
        potential_pks = []

        for col in df.columns:
            col_info = self.analyze_column(df_sample[col], col)
            columns.append(col_info)

            # Identify potential primary keys
            if col_info["is_potential_id"] and col_info["cardinality_ratio"] > 0.95:
                potential_pks.append(col)

        schema = {
            "filename": filepath.name,
            "filepath": str(filepath),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "sampled": sampled,
            "sample_size": len(df_sample),
            "columns": columns,
            "potential_primary_keys": potential_pks,
            "column_names": list(df.columns),
        }

        self.file_schemas[filepath.name] = schema
        return schema

    def find_column_alias_group(self, col_name: str) -> str | None:
        """
        Find which alias group a column belongs to.

        Args:
            col_name (str): The name of the column.

        Returns:
            str | None: The alias group name, or None if no match found.
        """
        col_lower = col_name.lower()

        for group, aliases in self.COLUMN_ALIASES.items():
            if any(
                alias.lower() == col_lower or alias.lower() in col_lower
                for alias in aliases
            ):
                return group
        return None

    def calculate_value_overlap(self, series1: pd.Series, series2: pd.Series) -> dict:
        """
        Calculate the overlap between two series' values.

        Args:
            series1 (pd.Series): The first column data.
            series2 (pd.Series): The second column data.

        Returns:
            dict: Overlap metrics including counts and percentages.
        """
        set1 = set(series1.dropna().astype(str).unique())

        set2 = set(series2.dropna().astype(str).unique())

        if not set1 or not set2:
            return {"overlap_count": 0, "overlap_percent_1": 0, "overlap_percent_2": 0}

        intersection = set1 & set2
        overlap_count = len(intersection)

        return {
            "overlap_count": overlap_count,
            "overlap_percent_1": round(overlap_count / len(set1) * 100, 2),
            "overlap_percent_2": round(overlap_count / len(set2) * 100, 2),
            "jaccard_similarity": round(len(intersection) / len(set1 | set2), 4),
        }

    def find_inter_file_relationships(self) -> list[dict]:
        """
        Find relationships between different files.

        Returns:
            list[dict]: List of discovered inter-file relationships.
        """
        print("\n" + "=" * 60)

        print("ANALYZING INTER-FILE RELATIONSHIPS")
        print("=" * 60)

        relationships = []
        files = list(self.file_schemas.keys())

        for i, file1 in enumerate(files):
            for file2 in files[i + 1 :]:
                schema1 = self.file_schemas[file1]
                schema2 = self.file_schemas[file2]
                df1 = self.dataframes.get(file1)
                df2 = self.dataframes.get(file2)

                if df1 is None or df2 is None:
                    continue

                # Check for matching column names
                common_cols = set(schema1["column_names"]) & set(
                    schema2["column_names"]
                )

                for col in common_cols:
                    overlap = self.calculate_value_overlap(df1[col], df2[col])

                    if (
                        overlap["overlap_count"] > 0
                        and overlap["jaccard_similarity"] > 0.1
                    ):
                        rel = {
                            "type": "exact_column_match",
                            "file1": file1,
                            "file2": file2,
                            "column": col,
                            "alias_group": self.find_column_alias_group(col),
                            **overlap,
                        }
                        relationships.append(rel)
                        print(
                            f"  Found: {file1} <-> {file2} via '{col}' "
                            f"(overlap: {overlap['overlap_count']}, "
                            f"jaccard: {overlap['jaccard_similarity']:.3f})"
                        )

                # Check for alias matches (different column names, same concept)
                for col1 in schema1["column_names"]:
                    group1 = self.find_column_alias_group(col1)
                    if not group1:
                        continue

                    for col2 in schema2["column_names"]:
                        if col1 == col2:  # Skip exact matches (already handled)
                            continue

                        group2 = self.find_column_alias_group(col2)
                        if group1 == group2:
                            overlap = self.calculate_value_overlap(df1[col1], df2[col2])

                            if (
                                overlap["overlap_count"] > 0
                                and overlap["jaccard_similarity"] > 0.05
                            ):
                                rel = {
                                    "type": "alias_match",
                                    "file1": file1,
                                    "file2": file2,
                                    "column1": col1,
                                    "column2": col2,
                                    "alias_group": group1,
                                    **overlap,
                                }
                                relationships.append(rel)
                                print(
                                    f"  Found: {file1}.{col1} <-> {file2}.{col2} "
                                    f"(alias: {group1}, jaccard: {overlap['jaccard_similarity']:.3f})"
                                )

        self.relationships = relationships
        return relationships

    def find_intra_file_relationships(self) -> dict[str, list[dict]]:
        """
        Find relationships within each file (column correlations, dependencies).

        Returns:
            dict[str, list[dict]]: Mapping of filenames to their intra-file relationships.
        """
        print("\n" + "=" * 60)

        print("ANALYZING INTRA-FILE RELATIONSHIPS")
        print("=" * 60)

        intra_rels = {}

        for filename, df in self.dataframes.items():
            print(f"\n  Analyzing: {filename}")
            file_rels = []

            # Get numeric columns for correlation
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_cols) >= 2:
                # Calculate correlation matrix
                try:
                    corr_matrix = df[numeric_cols].corr()

                    # Find highly correlated pairs
                    for i, col1 in enumerate(numeric_cols):
                        for col2 in numeric_cols[i + 1 :]:
                            corr = corr_matrix.loc[col1, col2]
                            if abs(corr) > 0.7 and not pd.isna(corr):
                                file_rels.append(
                                    {
                                        "type": "high_correlation",
                                        "column1": col1,
                                        "column2": col2,
                                        "correlation": round(float(corr), 4),
                                        "direction": "positive"
                                        if corr > 0
                                        else "negative",
                                    }
                                )
                                print(
                                    f"    Correlation: {col1} <-> {col2} = {corr:.3f}"
                                )
                except Exception as e:
                    print(f"    Warning: Could not calculate correlations: {e}")

            # Find functional dependencies (one column determines another)
            id_cols = [
                c
                for c in df.columns
                if any(p.lower() in c.lower() for p in self.ID_PATTERNS)
            ]

            for id_col in id_cols[:3]:  # Limit to first 3 ID columns
                try:
                    grouped = df.groupby(id_col).nunique()
                    for other_col in df.columns:
                        if other_col != id_col:
                            max_unique = grouped[other_col].max()
                            if max_unique == 1:
                                file_rels.append(
                                    {
                                        "type": "functional_dependency",
                                        "determinant": id_col,
                                        "dependent": other_col,
                                        "description": f"{id_col} uniquely determines {other_col}",
                                    }
                                )
                except Exception:
                    pass

            # Find temporal relationships

            date_cols = [
                c
                for c in df.columns
                if any(d in c.lower() for d in ["date", "time", "season", "year"])
            ]

            if date_cols:
                file_rels.append(
                    {
                        "type": "temporal_columns",
                        "columns": date_cols,
                        "description": "Columns that may represent time-based relationships",
                    }
                )

            intra_rels[filename] = file_rels

        self.intra_relationships = intra_rels
        return intra_rels

    def categorize_files(self) -> dict[str, list[str]]:
        """
        Categorize files by their apparent entity type.

        Returns:
            dict[str, list[str]]: Mapping of categories to lists of filenames.
        """
        categories = {
            "player_data": [],
            "team_data": [],
            "game_data": [],
            "schedule_data": [],
            "draft_data": [],
            "awards_data": [],
            "stats_data": [],
            "reference_data": [],
            "other": [],
        }

        for filename in self.file_schemas:
            name_lower = filename.lower()

            if "schedule" in name_lower:
                categories["schedule_data"].append(filename)
            elif "draft" in name_lower:
                categories["draft_data"].append(filename)
            elif (
                "award" in name_lower
                or "all-star" in name_lower
                or "championship" in name_lower
            ):
                categories["awards_data"].append(filename)
            elif "game" in name_lower:
                categories["game_data"].append(filename)
            elif any(p in name_lower for p in ["player", "players"]):
                categories["player_data"].append(filename)
            elif any(t in name_lower for t in ["team", "opponent"]):
                categories["team_data"].append(filename)
            elif any(
                s in name_lower
                for s in [
                    "stat",
                    "per game",
                    "totals",
                    "per 100",
                    "per 36",
                    "advanced",
                    "shooting",
                    "play by play",
                ]
            ):
                categories["stats_data"].append(filename)
            elif any(
                r in name_lower for r in ["official", "inactive", "line_score", "info"]
            ):
                categories["reference_data"].append(filename)
            else:
                categories["other"].append(filename)

        return categories

    def generate_entity_relationship_summary(self) -> dict:
        """
        Generate a summary of entity relationships.

        Returns:
            dict: Summary of central entities and relationship graph.
        """

        # Build relationship graph

        graph = defaultdict(lambda: defaultdict(list))

        for rel in self.relationships:
            file1, file2 = rel["file1"], rel["file2"]

            if rel["type"] == "exact_column_match":
                graph[file1][file2].append(
                    {"column": rel["column"], "strength": rel["jaccard_similarity"]}
                )
            else:
                graph[file1][file2].append(
                    {
                        "column1": rel["column1"],
                        "column2": rel["column2"],
                        "strength": rel["jaccard_similarity"],
                    }
                )

        # Find central entities (most connections)
        connection_counts = defaultdict(int)
        for file1 in graph:
            for file2 in graph[file1]:
                connection_counts[file1] += 1
                connection_counts[file2] += 1

        central_entities = sorted(connection_counts.items(), key=lambda x: -x[1])[:10]

        # Convert defaultdict to regular dict for JSON serialization
        graph_dict = {k: dict(v) for k, v in graph.items()}

        return {
            "relationship_graph": graph_dict,
            "central_entities": central_entities,
            "total_relationships": len(self.relationships),
        }

    def generate_report(self) -> dict:
        """
        Generate a comprehensive analysis report.

        Returns:
            dict: The complete analysis report.
        """
        categories = self.categorize_files()

        er_summary = self.generate_entity_relationship_summary()

        return {
            "metadata": {
                "generated_at": datetime.now(tz=UTC).isoformat(),
                "csv_directory": str(self.csv_dir),
                "total_files_analyzed": len(self.file_schemas),
                "sample_size_used": self.sample_size,
            },
            "file_categories": categories,
            "file_schemas": self.file_schemas,
            "inter_file_relationships": self.relationships,
            "intra_file_relationships": self.intra_relationships,
            "entity_relationship_summary": er_summary,
        }

    def print_summary(self, report: dict):  # noqa: PLR0912
        """
        Print a human-readable summary of the analysis.


        Args:
            report (dict): The analysis report to summarize.
        """
        print("\n" + "=" * 80)

        print("CSV RELATIONSHIP ANALYSIS SUMMARY")
        print("=" * 80)

        print(f"\nAnalysis completed at: {report['metadata']['generated_at']}")
        print(f"Total files analyzed: {report['metadata']['total_files_analyzed']}")

        # File categories
        print("\n" + "-" * 40)
        print("FILE CATEGORIES")
        print("-" * 40)
        for category, files in report["file_categories"].items():
            if files:
                print(f"\n{category.upper().replace('_', ' ')} ({len(files)} files):")
                for f in files:
                    schema = self.file_schemas.get(f, {})
                    rows = schema.get("total_rows", "N/A")
                    cols = schema.get("total_columns", "N/A")
                    print(f"  - {f} ({rows:,} rows, {cols} columns)")

        # Key relationships
        print("\n" + "-" * 40)
        print("KEY INTER-FILE RELATIONSHIPS")
        print("-" * 40)

        # Group by alias group
        by_group = defaultdict(list)
        for rel in report["inter_file_relationships"]:
            group = rel.get("alias_group", "other")
            by_group[group].append(rel)

        for group, rels in sorted(by_group.items(), key=lambda x: -len(x[1])):
            if group and len(rels) > 0:
                print(f"\n{group.upper()} relationships ({len(rels)} found):")
                # Show top 5 strongest relationships
                sorted_rels = sorted(
                    rels, key=lambda x: -x.get("jaccard_similarity", 0)
                )[:5]
                for rel in sorted_rels:
                    if rel["type"] == "exact_column_match":
                        print(f"  {rel['file1']} <-> {rel['file2']}")
                        print(
                            f"    Column: {rel['column']}, Jaccard: {rel['jaccard_similarity']:.3f}"
                        )
                    else:
                        print(
                            f"  {rel['file1']}.{rel['column1']} <-> {rel['file2']}.{rel['column2']}"
                        )
                        print(f"    Jaccard: {rel['jaccard_similarity']:.3f}")

        # Central entities
        print("\n" + "-" * 40)
        print("MOST CONNECTED FILES (Hub Entities)")
        print("-" * 40)
        for filename, count in report["entity_relationship_summary"][
            "central_entities"
        ]:
            print(f"  {filename}: {count} connections")

        # Intra-file highlights
        print("\n" + "-" * 40)
        print("INTRA-FILE HIGHLIGHTS")
        print("-" * 40)
        for filename, rels in report["intra_file_relationships"].items():
            correlations = [r for r in rels if r["type"] == "high_correlation"]
            if correlations:
                print(f"\n{filename}:")
                for corr in correlations[:3]:
                    print(
                        f"  - {corr['column1']} <-> {corr['column2']}: "
                        f"{corr['correlation']:.3f} ({corr['direction']})"
                    )

        # Schema summary
        print("\n" + "-" * 40)
        print("POTENTIAL PRIMARY KEYS BY FILE")
        print("-" * 40)
        for filename, schema in self.file_schemas.items():
            pks = schema.get("potential_primary_keys", [])
            if pks:
                print(f"  {filename}: {', '.join(pks)}")

    def run(self) -> dict:
        """
        Run the complete analysis pipeline.

        Returns:
            dict: The generated report.
        """
        print("=" * 60)

        print("CSV RELATIONSHIP ANALYZER")
        print("=" * 60)
        print(f"Directory: {self.csv_dir}")
        print(f"Sample size: {self.sample_size}")

        # Discover files
        files = self.discover_files()
        print(f"\nFound {len(files)} CSV files")

        # Analyze each file
        print("\n" + "-" * 40)
        print("ANALYZING FILE SCHEMAS")
        print("-" * 40)
        for filepath in files:
            self.analyze_file_schema(filepath)

        # Find relationships
        self.find_inter_file_relationships()
        self.find_intra_file_relationships()

        # Generate report
        report = self.generate_report()
        self.print_summary(report)

        return report


def json_serializer(obj):  # noqa: PLR0911
    """Custom JSON serializer for complex types."""

    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if pd.isna(obj):
        return None
    return str(obj)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze relationships between CSV files"
    )
    parser.add_argument(
        "--csv-dir",
        type=str,
        default="raw-data/csv",
        help="Path to directory containing CSV files",
    )
    parser.add_argument(
        "--output-dir", type=str, default=".", help="Directory to save output files"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=10000,
        help="Number of rows to sample for large files",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="csv_relationship_analysis.json",
        help="Output JSON filename",
    )

    args = parser.parse_args()

    # Resolve paths
    csv_dir = Path(args.csv_dir)
    if not csv_dir.is_absolute():
        # Try relative to script location
        script_dir = Path(__file__).parent.parent
        csv_dir = script_dir / args.csv_dir

    if not csv_dir.exists():
        print(f"Error: CSV directory not found: {csv_dir}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run analysis
    analyzer = CSVRelationshipAnalyzer(csv_dir, sample_size=args.sample_size)
    report = analyzer.run()

    # Save JSON report
    output_file = output_dir / args.output_json
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=json_serializer)

    print(f"\n{'=' * 60}")
    print(f"Full report saved to: {output_file}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

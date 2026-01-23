"""
Identity management for ETL.

Builds a bridge between Basketball Reference IDs (bref_id) and NBA API IDs (nba_id)
by joining staging data with a local SQLite database of NBA player info.
"""


def build_identity_bridge(con):
    """
    Construct the 'bridge_ids' table to link player identities across data sources.

    Attaches a secondary SQLite database containing NBA Common Player Info,
    and performs a fuzzy match (name + birthdate) to link players from
    Basketball Reference (staging_player_career_info) to official NBA IDs.

    Args:
        con (duckdb.DuckDBPyConnection): The DuckDB connection.
    """
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute("ATTACH 'raw-data/database/sqlite/nba.sqlite' AS nba (TYPE SQLITE);")

    con.execute("""
        INSERT INTO bridge_ids (bref_id, nba_id, name, birth_date)
        SELECT DISTINCT
            bref.player_id AS bref_id,
            CAST(nba_p.person_id AS VARCHAR) AS nba_id,
            bref.player AS name,
            TRY_CAST(bref.birth_date AS DATE) AS birth_date
        FROM staging_player_career_info bref
        JOIN nba.common_player_info nba_p
          ON trim(lower(replace(bref.player, '.', ''))) = trim(lower(replace(nba_p.display_first_last, '.', '')))
         AND TRY_CAST(bref.birth_date AS DATE) = TRY_CAST(nba_p.birthdate AS DATE)
        ON CONFLICT DO NOTHING
    """)

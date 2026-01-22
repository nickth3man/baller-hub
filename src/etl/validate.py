def validate_etl(con):
    """
    Validate ETL consistency and integrity for the fact_player_gamelogs table.
    
    Performs a parity check between the database table and a filtered CSV, validates the points calculation formula, and verifies referential integrity for player_id and team_id. If the database count is zero, logs a warning and returns early, skipping the strict validations. Each validation uses assertions and will raise an AssertionError on failure.
    
    Parameters:
        con: Database connection or cursor with an execute(sql).fetchone() API used to run validation queries.
    
    Raises:
        AssertionError: If the DB/CSV counts differ, if any records fail the points formula, or if any orphaned player or team records are found.
    """
    print("Starting validation...")

    db_count = con.execute("SELECT count(*) FROM fact_player_gamelogs").fetchone()[0]
    csv_count = con.execute("""
        SELECT count(*)
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Player Play By Play.csv', nullstr='NA') log
        JOIN bridge_ids b ON log.player = b.name
    """).fetchone()[0]

    print(f"Parity Check: DB Count = {db_count}, Filtered CSV Count = {csv_count}")
    assert db_count == csv_count, f"Count mismatch: DB={db_count}, CSV={csv_count}"

    if db_count == 0:
        print("WARNING: Fact table is empty. Skipping strict validation.")
        return

    invalid_pts_count = con.execute("""
        SELECT count(*)
        FROM fact_player_gamelogs
        WHERE points != (2 * (made_field_goals - made_three_point_field_goals) + 3 * made_three_point_field_goals + made_free_throws)
    """).fetchone()[0]

    print(f"Logic Check (Points Formula): {invalid_pts_count} invalid records")
    assert invalid_pts_count == 0, (
        f"Points formula validation failed: {invalid_pts_count} records"
    )

    orphaned_players = con.execute("""
        SELECT count(*)
        FROM fact_player_gamelogs f
        LEFT JOIN dim_players d ON f.player_id = d.bref_id
        WHERE d.bref_id IS NULL
    """).fetchone()[0]

    print(
        f"Referential Integrity Check (player_id): {orphaned_players} orphaned records"
    )
    assert orphaned_players == 0, (
        f"Referential integrity failed: {orphaned_players} player records"
    )

    orphaned_teams = con.execute("""
        SELECT count(*)
        FROM fact_player_gamelogs f
        LEFT JOIN dim_teams d ON f.team_id = d.bref_id
        WHERE d.bref_id IS NULL
    """).fetchone()[0]

    print(f"Referential Integrity Check (team_id): {orphaned_teams} orphaned records")
    assert orphaned_teams == 0, (
        f"Referential integrity failed: {orphaned_teams} team records"
    )

    print("Validation successful!")
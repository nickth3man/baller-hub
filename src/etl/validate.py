def validate_etl(con):
    print("Starting validation...")

    db_count = con.execute("SELECT count(*) FROM fact_player_gamelogs").fetchone()[0]
    csv_count = con.execute("""
        SELECT count(*)
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Player Play By Play.csv') log
        JOIN bridge_ids b ON log.player = b.name
    """).fetchone()[0]

    print(f"Parity Check: DB Count = {db_count}, Filtered CSV Count = {csv_count}")
    assert db_count == csv_count, f"Count mismatch: DB={db_count}, CSV={csv_count}"
    assert db_count > 0, "Fact table is empty"

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

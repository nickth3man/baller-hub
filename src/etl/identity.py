def build_identity_bridge(con):
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute("ATTACH 'raw-data/database/sqlite/nba.sqlite' AS nba (TYPE SQLITE);")

    con.execute("""
        INSERT INTO bridge_ids (bref_id, nba_id, name, birth_date)
        SELECT DISTINCT
            bref.player_id AS bref_id,
            CAST(nba_p.person_id AS VARCHAR) AS nba_id,
            bref.player AS name,
            CAST(bref.birth_date AS DATE) AS birth_date
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Player Career Info.csv') bref
        JOIN nba.common_player_info nba_p
          ON trim(lower(replace(bref.player, '.', ''))) = trim(lower(replace(nba_p.display_first_last, '.', '')))
         AND CAST(bref.birth_date AS DATE) = CAST(nba_p.birthdate AS DATE)
    """)

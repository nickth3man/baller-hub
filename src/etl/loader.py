def load_dims(con):
    con.execute("""
        INSERT INTO dim_players (bref_id, nba_id, name, birth_date)
        SELECT DISTINCT bref_id, nba_id, name, birth_date
        FROM bridge_ids
        ON CONFLICT DO NOTHING
    """)

    con.execute("""
        INSERT INTO dim_teams (bref_id, nba_id, abbreviation)
        SELECT team AS bref_id, NULL AS nba_id, team AS abbreviation
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Player Play By Play.csv', nullstr='NA')
        GROUP BY team
        ON CONFLICT DO NOTHING
    """)


def load_facts(con):
    con.execute("""
        INSERT INTO fact_player_gamelogs (
            player_id, team_id, game_id, date, minutes_played,
            made_field_goals, attempted_field_goals,
            made_three_point_field_goals, attempted_three_point_field_goals,
            made_free_throws, attempted_free_throws,
            offensive_rebounds, defensive_rebounds,
            assists, steals, blocks, turnovers, personal_fouls, points
        )
        SELECT
            b.bref_id AS player_id,
            log.team AS team_id,
            log.season || '-' || log.team || '-' || log.player_id AS game_id,
            CAST(log.season || '-01-01' AS DATE) AS date,
            log.mp AS minutes_played,
            CAST(tot.fg AS INTEGER) AS made_field_goals,
            CAST(tot.fga AS INTEGER) AS attempted_field_goals,
            CAST(tot.x3p AS INTEGER) AS made_three_point_field_goals,
            CAST(tot.x3pa AS INTEGER) AS attempted_three_point_field_goals,
            CAST(tot.ft AS INTEGER) AS made_free_throws,
            CAST(tot.fta AS INTEGER) AS attempted_free_throws,
            CAST(tot.orb AS INTEGER) AS offensive_rebounds,
            CAST(tot.drb AS INTEGER) AS defensive_rebounds,
            CAST(tot.ast AS INTEGER) AS assists,
            CAST(tot.stl AS INTEGER) AS steals,
            CAST(tot.blk AS INTEGER) AS blocks,
            CAST(tot.tov AS INTEGER) AS turnovers,
            CAST(tot.pf AS INTEGER) AS personal_fouls,
            CAST(tot.pts AS INTEGER) AS points
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Player Play By Play.csv', nullstr='NA') log
        JOIN read_csv_auto('raw-data/misc-csv/csv_2/Player Totals.csv', nullstr='NA') tot
          ON log.player_id = tot.player_id AND log.season = tot.season AND log.team = tot.team
        JOIN bridge_ids b ON log.player = b.name
        ON CONFLICT DO NOTHING
    """)

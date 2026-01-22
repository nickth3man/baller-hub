def load_dims(con):
    con.execute("""
        INSERT INTO dim_players (bref_id, nba_id, name, birth_date)
        SELECT DISTINCT bref_id, nba_id, name, birth_date
        FROM bridge_ids
        ON CONFLICT DO NOTHING
    """)

    con.execute("""
        INSERT INTO dim_teams (bref_id, nba_id, abbreviation)
        SELECT team AS bref_id, NULL AS nba_id, abbrev AS abbreviation
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Team Abbrev.csv')
        GROUP BY team, abbrev
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
            log.tm AS team_id,
            log.date || '-' || log.tm || '-' || log.opp AS game_id,
            CAST(log.date AS DATE) AS date,
            log.mp AS minutes_played,
            CAST(log.fg AS INTEGER) AS made_field_goals,
            CAST(log.fga AS INTEGER) AS attempted_field_goals,
            CAST(log."3p" AS INTEGER) AS made_three_point_field_goals,
            CAST(log."3pa" AS INTEGER) AS attempted_three_point_field_goals,
            CAST(log.ft AS INTEGER) AS made_free_throws,
            CAST(log.fta AS INTEGER) AS attempted_free_throws,
            CAST(log.orb AS INTEGER) AS offensive_rebounds,
            CAST(log.drb AS INTEGER) AS defensive_rebounds,
            CAST(log.ast AS INTEGER) AS assists,
            CAST(log.stl AS INTEGER) AS steals,
            CAST(log.blk AS INTEGER) AS blocks,
            CAST(log.tov AS INTEGER) AS turnovers,
            CAST(log.pf AS INTEGER) AS personal_fouls,
            CAST(log.pts AS INTEGER) AS points
        FROM read_csv_auto('raw-data/misc-csv/csv_2/Player Play By Play.csv') log
        JOIN bridge_ids b ON log.player = b.name
        ON CONFLICT DO NOTHING
    """)

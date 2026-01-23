-- Baller Hub Database Schema
-- PostgreSQL-compatible DDL
-- Basketball Reference data structure

-- =====================================================
-- Players Table
-- =====================================================
CREATE TABLE players (
    person_id VARCHAR(12) PRIMARY KEY,
    player_slug VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    height_string VARCHAR(10),  -- e.g., "6-6"
    height_inches INT,
    weight INT,
    draft_year INT,
    draft_round INT,
    draft_number INT,
    from_year INT,
    to_year INT,
    is_hof BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for players
CREATE INDEX idx_players_player_slug ON players(player_slug);
CREATE INDEX idx_players_name ON players(last_name, first_name);
CREATE INDEX idx_players_hof ON players(is_hOF) WHERE is_hof = TRUE;
CREATE INDEX idx_players_active_years ON players(from_year, to_year);

-- =====================================================
-- Teams Table
-- =====================================================
CREATE TABLE teams (
    team_id VARCHAR(50) PRIMARY KEY,  -- Basketball Reference team abbreviation (e.g., "LAL")
    abbreviation VARCHAR(5) UNIQUE NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    year_founded INT,
    arena VARCHAR(100),
    arena_capacity INT,
    owner VARCHAR(100),
    general_manager VARCHAR(100),
    head_coach VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for teams
CREATE INDEX idx_teams_abbreviation ON teams(abbreviation);
CREATE INDEX idx_teams_nickname ON teams(nickname);
CREATE INDEX idx_teams_city ON teams(city);

-- =====================================================
-- Games Table
-- =====================================================
CREATE TABLE games (
    game_id VARCHAR(50) PRIMARY KEY,  -- Composite ID (e.g., "202401010LAL")
    season_id VARCHAR(10) NOT NULL,    -- e.g., "2023-24"
    game_date DATE NOT NULL,
    home_team_id VARCHAR(50) NOT NULL,
    away_team_id VARCHAR(50) NOT NULL,
    home_score INT,
    away_score INT,
    winner_id VARCHAR(50),            -- Team ID of winner (can be derived from scores)
    game_type VARCHAR(20) NOT NULL DEFAULT 'Regular Season',  -- 'Regular Season', 'Playoffs', 'Preseason'
    attendance INT,
    arena_id VARCHAR(50),             -- Reference to arena name or ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    CONSTRAINT fk_games_home_team FOREIGN KEY (home_team_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
    CONSTRAINT fk_games_away_team FOREIGN KEY (away_team_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
    CONSTRAINT fk_games_winner FOREIGN KEY (winner_id) REFERENCES teams(team_id) ON DELETE SET NULL,

    -- Check constraints
    CONSTRAINT chk_home_away_different CHECK (home_team_id != away_team_id),
    CONSTRAINT chk_game_type CHECK (game_type IN ('Regular Season', 'Playoffs', 'Preseason', 'All-Star')),
    CONSTRAINT chk_scores CHECK (home_score IS NULL OR away_score IS NULL OR (home_score >= 0 AND away_score >= 0))
);

-- Indexes for games
CREATE INDEX idx_games_season ON games(season_id);
CREATE INDEX idx_games_date ON games(game_date);
CREATE INDEX idx_games_home_team ON games(home_team_id);
CREATE INDEX idx_games_away_team ON games(away_team_id);
CREATE INDEX idx_games_winner ON games(winner_id);
CREATE INDEX idx_games_type ON games(game_type);
CREATE INDEX idx_games_team_lookup ON games(home_team_id, game_date);
CREATE INDEX idx_games_season_date ON games(season_id, game_date);

-- =====================================================
-- Player Game Stats Table
-- =====================================================
CREATE TABLE player_game_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    game_id VARCHAR(50) NOT NULL,
    minutes_played VARCHAR(10),  -- Store as string like "34:25" or decimal like "34.42"
    pts INT DEFAULT 0,           -- Points
    ast INT DEFAULT 0,           -- Assists
    blk INT DEFAULT 0,           -- Blocks
    stl INT DEFAULT 0,           -- Steals
    fgm INT DEFAULT 0,           -- Field Goals Made
    fga INT DEFAULT 0,           -- Field Goals Attempted
    fg3m INT DEFAULT 0,          -- 3-Point Field Goals Made
    fg3a INT DEFAULT 0,          -- 3-Point Field Goals Attempted
    ftm INT DEFAULT 0,           -- Free Throws Made
    fta INT DEFAULT 0,           -- Free Throws Attempted
    reb INT DEFAULT 0,           -- Total Rebounds
    tov INT DEFAULT 0,           -- Turnovers
    plus_minus INT DEFAULT 0,    -- Plus/Minus rating
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    CONSTRAINT fk_pgs_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE,
    CONSTRAINT fk_pgs_game FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,

    -- Unique constraint: one stat record per player per game
    CONSTRAINT uq_player_game UNIQUE (player_id, game_id),

    -- Check constraints
    CONSTRAINT chk_shots_valid CHECK (
        (fgm >= 0 AND fga >= 0 AND fgm <= fga) AND
        (fg3m >= 0 AND fg3a >= 0 AND fg3m <= fg3a) AND
        (ftm >= 0 AND fta >= 0 AND ftm <= fta) AND
        (fg3m <= fgm)  -- 3-pointers can't exceed total field goals
    )
);

-- Indexes for player_game_stats
CREATE INDEX idx_pgs_player ON player_game_stats(player_id);
CREATE INDEX idx_pgs_game ON player_game_stats(game_id);
CREATE INDEX idx_pgs_player_season ON player_game_stats(player_id, game_id);
CREATE INDEX idx_pgs_pts ON player_game_stats(pts);
CREATE INDEX idx_pgs_reb ON player_game_stats(reb);
CREATE INDEX idx_pgs_ast ON player_game_stats(ast);

-- =====================================================
-- Player Season Stats Table
-- =====================================================
CREATE TABLE player_season_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    season VARCHAR(10) NOT NULL,   -- e.g., "2023-24"
    team_id VARCHAR(50),
    games_played INT DEFAULT 0,
    games_started INT DEFAULT 0,
    minutes_played NUMERIC(8,2) DEFAULT 0,  -- Total minutes in season
    points NUMERIC(8,1) DEFAULT 0,
    rebounds_total NUMERIC(8,1) DEFAULT 0,
    assists NUMERIC(8,1) DEFAULT 0,
    steals NUMERIC(8,1) DEFAULT 0,
    blocks NUMERIC(8,1) DEFAULT 0,
    turnovers NUMERIC(8,1) DEFAULT 0,
    personal_fouls NUMERIC(8,1) DEFAULT 0,
    field_goals_made INT DEFAULT 0,
    field_goals_attempted INT DEFAULT 0,
    three_pointers_made INT DEFAULT 0,
    three_pointers_attempted INT DEFAULT 0,
    free_throws_made INT DEFAULT 0,
    free_throws_attempted INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    CONSTRAINT fk_pss_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE,
    CONSTRAINT fk_pss_team FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL,

    -- Unique constraint: one stat record per player per season
    CONSTRAINT uq_player_season UNIQUE (player_id, season, team_id),

    -- Check constraints
    CONSTRAINT chk_games_valid CHECK (
        games_played >= 0 AND
        games_started >= 0 AND
        games_started <= games_played
    ),
    CONSTRAINT chk_season_stats_valid CHECK (
        minutes_played >= 0 AND
        points >= 0 AND
        rebounds_total >= 0 AND
        assists >= 0 AND
        steals >= 0 AND
        blocks >= 0 AND
        turnovers >= 0 AND
        personal_fouls >= 0
    ),
    CONSTRAINT chk_fg_stats_valid CHECK (
        field_goals_made >= 0 AND
        field_goals_attempted >= 0 AND
        field_goals_made <= field_goals_attempted AND
        three_pointers_made >= 0 AND
        three_pointers_attempted >= 0 AND
        three_pointers_made <= three_pointers_attempted AND
        three_pointers_made <= field_goals_made AND
        free_throws_made >= 0 AND
        free_throws_attempted >= 0 AND
        free_throws_made <= free_throws_attempted
    )
);

-- Indexes for player_season_stats
CREATE INDEX idx_pss_player ON player_season_stats(player_id);
CREATE INDEX idx_pss_season ON player_season_stats(season);
CREATE INDEX idx_pss_team ON player_season_stats(team_id);
CREATE INDEX idx_pss_player_season ON player_season_stats(player_id, season);
CREATE INDEX idx_pss_team_season ON player_season_stats(team_id, season);
CREATE INDEX idx_pss_points ON player_season_stats(points);
CREATE INDEX idx_pss_rebounds ON player_season_stats(rebounds_total);
CREATE INDEX idx_pss_assists ON player_season_stats(assists);

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- View: Player summary with career stats
CREATE VIEW player_career_summary AS
SELECT
    p.person_id,
    p.player_slug,
    p.first_name,
    p.last_name,
    COUNT(DISTINCT pss.season) AS seasons_played,
    SUM(pss.games_played) AS career_games,
    SUM(pss.points) AS career_points,
    SUM(pss.rebounds_total) AS career_rebounds,
    SUM(pss.assists) AS career_assists,
    ROUND(AVG(pss.points) FILTER (WHERE pss.games_played > 0), 1) AS avg_points_per_game,
    ROUND(AVG(pss.rebounds_total) FILTER (WHERE pss.games_played > 0), 1) AS avg_rebounds_per_game,
    ROUND(AVG(pss.assists) FILTER (WHERE pss.games_played > 0), 1) AS avg_assists_per_game,
    p.is_hof
FROM players p
LEFT JOIN player_season_stats pss ON p.person_id = pss.player_id
GROUP BY p.person_id, p.player_slug, p.first_name, p.last_name, p.is_hof;

-- View: Game summary with team names
CREATE VIEW game_summary AS
SELECT
    g.game_id,
    g.season_id,
    g.game_date,
    g.game_type,
    t_home.full_name AS home_team_name,
    g.home_score,
    t_away.full_name AS away_team_name,
    g.away_score,
    t_winner.full_name AS winner_team_name,
    g.attendance,
    g.arena_id
FROM games g
JOIN teams t_home ON g.home_team_id = t_home.team_id
JOIN teams t_away ON g.away_team_id = t_away.team_id
LEFT JOIN teams t_winner ON g.winner_id = t_winner.team_id;

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_players_updated_at
    BEFORE UPDATE ON players
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_games_updated_at
    BEFORE UPDATE ON games
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_player_game_stats_updated_at
    BEFORE UPDATE ON player_game_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_player_season_stats_updated_at
    BEFORE UPDATE ON player_season_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Comments for documentation
-- =====================================================

COMMENT ON TABLE players IS 'Player biographical information from Basketball Reference';
COMMENT ON TABLE teams IS 'NBA team information including franchise details';
COMMENT ON TABLE games IS 'Game schedule and results';
COMMENT ON TABLE player_game_stats IS 'Individual player statistics per game';
COMMENT ON TABLE player_season_stats IS 'Aggregated player statistics per season';

COMMENT ON COLUMN games.winner_id IS 'Team ID of the winning team (can be NULL if game not yet played)';
COMMENT ON COLUMN player_game_stats.minutes_played IS 'Minutes played as string (e.g., "34:25") for exact time or decimal for approximate';
COMMENT ON COLUMN players.height_inches IS 'Player height in inches for easier querying';
COMMENT ON COLUMN games.game_type IS 'Type of game: Regular Season, Playoffs, Preseason, or All-Star';

-- =====================================================
-- Sample Data (Optional - for testing)
-- =====================================================

-- Note: Remove this section before production deployment

-- INSERT INTO teams (team_id, abbreviation, nickname, full_name, city, year_founded, arena, arena_capacity, owner, general_manager, head_coach)
-- VALUES
--     ('LAL', 'LAL', 'Lakers', 'Los Angeles Lakers', 'Los Angeles', 1947, 'Crypto.com Arena', 19907, 'Jeanie Buss', 'Rob Pelinka', 'JJ Redick'),
--     ('BOS', 'BOS', 'Celtics', 'Boston Celtics', 'Boston', 1946, 'TD Garden', 18624, 'Wyc Grousbeck', 'Brad Stevens', 'Joe Mazzulla'),
--     ('GSW', 'GSW', 'Warriors', 'Golden State Warriors', 'San Francisco', 1946, 'Chase Center', 18064, 'Joe Lacob', 'Mike Dunleavy Jr.', 'Steve Kerr');

-- INSERT INTO players (person_id, player_slug, first_name, last_name, birth_date, height_string, height_inches, weight, from_year, to_year, is_hof)
-- VALUES
--     ('abdulka01', 'abdulka01', 'Kareem', 'Abdul-Jabbar', '1947-04-16', '7-2', 86, 225, 1969, 1989, TRUE),
--     ('jamesle01', 'jamesle01', 'LeBron', 'James', '1984-12-30', '6-9', 81, 250, 2003, 2024, FALSE),
--     ('curryst01', 'curryst01', 'Stephen', 'Curry', '1988-03-14', '6-2', 74, 185, 2009, 2024, FALSE);

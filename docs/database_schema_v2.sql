-- Baller Hub Database Schema V2
-- PostgreSQL-compatible DDL
-- Target: Basketball-Reference 1:1 Mirror
-- Generated: 2026-01-22

-- =====================================================
-- 1. Core Entities (Franchises, Teams, Players, Games)
-- =====================================================

-- 1.1 Franchises (Legal Entity History)
CREATE TABLE franchises (
    franchise_id VARCHAR(10) PRIMARY KEY, -- e.g., "LAL", "ATL"
    full_name VARCHAR(100) NOT NULL,      -- Canonical/Current name
    city VARCHAR(50) NOT NULL,
    year_founded INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 Team Seasons (Yearly Iterations)
CREATE TABLE team_seasons (
    season_id VARCHAR(10) NOT NULL,       -- e.g., "2023-24"
    franchise_id VARCHAR(10) NOT NULL,
    team_name VARCHAR(100) NOT NULL,      -- Specific name for that season (e.g., "Seattle SuperSonics")
    abbreviation VARCHAR(5) NOT NULL,     -- e.g., "SEA"
    head_coach VARCHAR(100),
    general_manager VARCHAR(100),
    owner VARCHAR(100),
    arena VARCHAR(100),
    arena_capacity INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (season_id, franchise_id),
    CONSTRAINT fk_team_season_franchise FOREIGN KEY (franchise_id) REFERENCES franchises(franchise_id) ON DELETE CASCADE
);

-- 1.3 Players (Biographical Data)
CREATE TABLE players (
    person_id VARCHAR(12) PRIMARY KEY,    -- NBA.com ID (if using) or BBRef ID
    player_slug VARCHAR(50) UNIQUE NOT NULL, -- BBRef Slug (e.g., "jamesle01")
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    height_string VARCHAR(10),
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

-- 1.4 Games (Schedule & Results)
CREATE TABLE games (
    game_id VARCHAR(50) PRIMARY KEY,      -- e.g., "202310240DEN"
    season_id VARCHAR(10) NOT NULL,
    game_date DATE NOT NULL,
    home_franchise_id VARCHAR(10) NOT NULL,
    away_franchise_id VARCHAR(10) NOT NULL,
    home_score INT,
    away_score INT,
    winner_franchise_id VARCHAR(10),
    game_type VARCHAR(20) DEFAULT 'Regular Season',
    attendance INT,
    arena_id VARCHAR(50),
    duration_minutes INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_game_home FOREIGN KEY (home_franchise_id) REFERENCES franchises(franchise_id),
    CONSTRAINT fk_game_away FOREIGN KEY (away_franchise_id) REFERENCES franchises(franchise_id),
    CONSTRAINT fk_game_winner FOREIGN KEY (winner_franchise_id) REFERENCES franchises(franchise_id)
);

-- =====================================================
-- 2. Team Statistics
-- =====================================================

CREATE TABLE team_season_stats (
    season_id VARCHAR(10) NOT NULL,
    franchise_id VARCHAR(10) NOT NULL,
    
    -- Record
    games_played INT,
    wins INT,
    losses INT,
    win_percentage NUMERIC(5,3),
    
    -- Ratings (from Team Summaries.csv)
    mov NUMERIC(5,2),        -- Margin of Victory
    sos NUMERIC(5,2),        -- Strength of Schedule
    srs NUMERIC(5,2),        -- Simple Rating System
    offensive_rating NUMERIC(5,1),
    defensive_rating NUMERIC(5,1),
    net_rating NUMERIC(5,1),
    pace NUMERIC(5,1),
    
    -- Factors
    free_throw_rate NUMERIC(5,3),
    three_point_attempt_rate NUMERIC(5,3),
    true_shooting_percentage NUMERIC(5,3),
    effective_fg_percentage NUMERIC(5,3),
    turnover_percentage NUMERIC(5,1),
    offensive_rebound_percentage NUMERIC(5,1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (season_id, franchise_id),
    CONSTRAINT fk_team_stats_season FOREIGN KEY (season_id, franchise_id) REFERENCES team_seasons(season_id, franchise_id)
);

-- =====================================================
-- 3. Player Statistics (Season Level)
-- =====================================================

-- 3.1 Player Season Totals (Base Counting Stats)
CREATE TABLE player_season_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    season_id VARCHAR(10) NOT NULL,
    franchise_id VARCHAR(10),             -- Can be NULL for "TOT" rows
    team_abbrev VARCHAR(5),               -- "TOT", "LAL", etc.
    
    games_played INT,
    games_started INT,
    minutes_played INT,                   -- Total minutes
    
    field_goals_made INT,
    field_goals_attempted INT,
    three_pointers_made INT,
    three_pointers_attempted INT,
    two_pointers_made INT,
    two_pointers_attempted INT,
    free_throws_made INT,
    free_throws_attempted INT,
    
    offensive_rebounds INT,
    defensive_rebounds INT,
    total_rebounds INT,
    assists INT,
    steals INT,
    blocks INT,
    turnovers INT,
    personal_fouls INT,
    points INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_pss_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE,
    CONSTRAINT fk_pss_franchise FOREIGN KEY (franchise_id) REFERENCES franchises(franchise_id)
);

-- 3.2 Player Advanced Stats (from Advanced.csv)
CREATE TABLE player_season_advanced (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    season_id VARCHAR(10) NOT NULL,
    franchise_id VARCHAR(10),
    
    per NUMERIC(5,1),                     -- Player Efficiency Rating
    true_shooting_percentage NUMERIC(5,3),
    three_point_attempt_rate NUMERIC(5,3),
    free_throw_rate NUMERIC(5,3),
    
    offensive_rebound_percentage NUMERIC(5,1),
    defensive_rebound_percentage NUMERIC(5,1),
    total_rebound_percentage NUMERIC(5,1),
    assist_percentage NUMERIC(5,1),
    steal_percentage NUMERIC(5,1),
    block_percentage NUMERIC(5,1),
    turnover_percentage NUMERIC(5,1),
    usage_percentage NUMERIC(5,1),
    
    offensive_win_shares NUMERIC(5,1),
    defensive_win_shares NUMERIC(5,1),
    win_shares NUMERIC(5,1),
    win_shares_per_48 NUMERIC(5,3),
    
    offensive_box_plus_minus NUMERIC(5,1),
    defensive_box_plus_minus NUMERIC(5,1),
    box_plus_minus NUMERIC(5,1),
    vorp NUMERIC(5,1),                    -- Value Over Replacement Player
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_psa_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE
);

-- 3.3 Player Shooting Splits (from Player Shooting.csv)
CREATE TABLE player_season_shooting (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    season_id VARCHAR(10) NOT NULL,
    franchise_id VARCHAR(10),
    
    avg_dist_fga NUMERIC(5,1),
    
    -- % of FGA by Distance
    percent_fga_2p NUMERIC(5,3),
    percent_fga_0_3 NUMERIC(5,3),
    percent_fga_3_10 NUMERIC(5,3),
    percent_fga_10_16 NUMERIC(5,3),
    percent_fga_16_3p NUMERIC(5,3),
    percent_fga_3p NUMERIC(5,3),
    
    -- FG% by Distance
    fg_percent_2p NUMERIC(5,3),
    fg_percent_0_3 NUMERIC(5,3),
    fg_percent_3_10 NUMERIC(5,3),
    fg_percent_10_16 NUMERIC(5,3),
    fg_percent_16_3p NUMERIC(5,3),
    fg_percent_3p NUMERIC(5,3),
    
    -- Assisted %
    percent_assisted_2p NUMERIC(5,3),
    percent_assisted_3p NUMERIC(5,3),
    
    -- Dunks & Corner 3s
    percent_dunks_of_fga NUMERIC(5,3),
    num_dunks INT,
    percent_corner_3s_of_3pa NUMERIC(5,3),
    corner_3_point_percent NUMERIC(5,3),
    
    -- Heaves
    num_heaves_attempted INT,
    num_heaves_made INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_pssh_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE
);

-- 3.4 Player Play-by-Play / Impact (from Player Play By Play.csv)
CREATE TABLE player_season_play_by_play (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    season_id VARCHAR(10) NOT NULL,
    franchise_id VARCHAR(10),
    
    -- Position Estimates (%)
    pg_percent INT,
    sg_percent INT,
    sf_percent INT,
    pf_percent INT,
    c_percent INT,
    
    -- Plus/Minus Impact
    on_court_plus_minus_per_100 NUMERIC(5,1),
    net_plus_minus_per_100 NUMERIC(5,1),
    
    -- Turnover Details
    bad_pass_turnovers INT,
    lost_ball_turnovers INT,
    
    -- Foul Details
    shooting_fouls_committed INT,
    offensive_fouls_committed INT,
    shooting_fouls_drawn INT,
    offensive_fouls_drawn INT,
    
    -- Misc
    points_generated_by_assists INT,
    and1s INT,
    fga_blocked INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_pspbp_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE
);

-- =====================================================
-- 4. Game Logs / Box Scores
-- =====================================================

CREATE TABLE player_game_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(12) NOT NULL,
    game_id VARCHAR(50) NOT NULL,
    franchise_id VARCHAR(10) NOT NULL,
    
    minutes_played NUMERIC(5,2),
    
    -- Basic Box Score
    pts INT, ast INT, reb INT, 
    blk INT, stl INT, tov INT,
    fgm INT, fga INT,
    fg3m INT, fg3a INT,
    ftm INT, fta INT,
    plus_minus INT,
    
    -- Potential Advanced Game Stats (if available later)
    game_score NUMERIC(4,1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_pgs_player FOREIGN KEY (player_id) REFERENCES players(person_id) ON DELETE CASCADE,
    CONSTRAINT fk_pgs_game FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
    CONSTRAINT fk_pgs_franchise FOREIGN KEY (franchise_id) REFERENCES franchises(franchise_id),
    CONSTRAINT uq_player_game UNIQUE (player_id, game_id)
);

-- =====================================================
-- 5. Triggers for Timestamps
-- =====================================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables
CREATE TRIGGER update_franchises_modtime BEFORE UPDATE ON franchises FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_team_seasons_modtime BEFORE UPDATE ON team_seasons FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_players_modtime BEFORE UPDATE ON players FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_games_modtime BEFORE UPDATE ON games FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_team_stats_modtime BEFORE UPDATE ON team_season_stats FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_player_stats_modtime BEFORE UPDATE ON player_season_stats FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_player_adv_modtime BEFORE UPDATE ON player_season_advanced FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_player_shoot_modtime BEFORE UPDATE ON player_season_shooting FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_player_pbp_modtime BEFORE UPDATE ON player_season_play_by_play FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_player_game_modtime BEFORE UPDATE ON player_game_stats FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- =====================================================
-- 6. Indexes for Performance
-- =====================================================

CREATE INDEX idx_players_slug ON players(player_slug);
CREATE INDEX idx_games_season ON games(season_id);
CREATE INDEX idx_player_stats_season ON player_season_stats(season_id);
CREATE INDEX idx_player_stats_lookup ON player_season_stats(player_id, season_id);
CREATE INDEX idx_team_seasons_lookup ON team_seasons(franchise_id, season_id);

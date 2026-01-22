## Star Schema Bridging
- Decided to use DuckDB Views in 'init_db' to map 'dim_players', 'dim_teams', and 'fact_player_gamelogs' to the tables expected by the backend ('player', 'team', 'player_season', etc.).
- This avoids massive refactoring of the backend service layer and models while enabling the app to load data from the newly migrated database.

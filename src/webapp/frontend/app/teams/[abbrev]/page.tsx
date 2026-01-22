import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getTeam,
  getTeamHistory,
  getTeamRoster,
  getTeamSchedule,
  getTeamStats,
  RosterPlayer,
  Team,
  TeamHistorySeason,
  TeamScheduleGame,
  TeamSeasonStats,
} from "@/lib/api";

interface PageProps {
  params: Promise<{ abbrev: string }>;
}

const now = new Date();
const currentSeasonYear =
  now.getMonth() >= 9 ? now.getFullYear() + 1 : now.getFullYear();

function TeamHeader({ team }: { team: Team }) {
  return (
    <div className="mb-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-orange-600 p-6 text-white shadow-xl">
      <div className="flex flex-col items-start gap-6 md:flex-row md:items-center">
        <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-white/10 font-display text-4xl uppercase">
          {team.abbreviation}
        </div>

        <div className="flex-1">
          <h1 className="mb-1 font-display text-4xl uppercase tracking-[0.1em]">
            {team.city} {team.name}
          </h1>
          <p className="text-orange-100">
            {team.arena && `${team.arena}`}
            {team.arena_capacity &&
              ` - Capacity: ${team.arena_capacity.toLocaleString()}`}
          </p>
          <p className="mt-1 text-sm text-orange-200">
            Est. {team.founded_year}
            {team.franchise && ` - ${team.franchise.name} Franchise`}
          </p>
        </div>
      </div>
    </div>
  );
}

function RosterTable({ roster }: { roster: RosterPlayer[] }) {
  return (
    <div className="mb-6 overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="flex items-center justify-between bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Current Roster</h2>
        <span className="text-xs uppercase tracking-[0.2em] text-orange-200">
          {currentSeasonYear} Season
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Player</th>
              <th className="px-3 py-3 text-center">Pos</th>
              <th className="px-3 py-3 text-center">GP</th>
              <th className="px-3 py-3 text-center">GS</th>
              <th className="px-3 py-3 text-center">PPG</th>
            </tr>
          </thead>
          <tbody>
            {roster.map((player, idx) => (
              <tr
                key={player.player_id}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/players/${player.slug}`}
                    className="font-medium text-blue-600 hover:text-blue-800"
                  >
                    {player.name}
                  </Link>
                </td>
                <td className="px-3 py-3 text-center text-gray-600">
                  {player.position
                    ? player.position
                        .replace("_", " ")
                        .split(" ")
                        .map((word) => word[0])
                        .join("")
                    : "-"}
                </td>
                <td className="px-3 py-3 text-center">{player.games_played}</td>
                <td className="px-3 py-3 text-center">
                  {player.games_started}
                </td>
                <td className="px-3 py-3 text-center font-medium">
                  {player.ppg !== null && player.ppg !== undefined
                    ? player.ppg.toFixed(1)
                    : "-"}
                </td>
              </tr>
            ))}
            {roster.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No roster data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TeamStats({ stats }: { stats: TeamSeasonStats | null }) {
  if (!stats) {
    return (
      <div className="mb-6 rounded-lg bg-white p-6 shadow-md">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Season Stats
        </h2>
        <p className="text-sm text-gray-500">
          Stats unavailable for this season.
        </p>
      </div>
    );
  }

  return (
    <div className="mb-6 rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Season Stats</h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">{stats.wins}</p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Wins
          </p>
        </div>
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">{stats.losses}</p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Losses
          </p>
        </div>
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">
            {stats.points_per_game?.toFixed(1) ?? "-"}
          </p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            PPG
          </p>
        </div>
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">
            {stats.points_allowed_per_game?.toFixed(1) ?? "-"}
          </p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Opp PPG
          </p>
        </div>
      </div>
    </div>
  );
}

function RecentGames({ games }: { games: TeamScheduleGame[] }) {
  const recentGames = games.slice(-5).reverse();
  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Recent Games</h2>
      <div className="space-y-3">
        {recentGames.map((game) => (
          <div
            key={game.game_id}
            className="flex items-center justify-between text-sm"
          >
            <div className="font-medium text-gray-900">
              {game.location === "HOME" ? "vs" : "@"} {game.opponent_abbrev}
            </div>
            <div className="text-gray-500">
              {game.team_score !== null && game.team_score !== undefined
                ? `${game.team_score}-${game.opponent_score}`
                : "TBD"}
            </div>
            <div className="text-gray-400">{game.result ?? "-"}</div>
          </div>
        ))}
        {recentGames.length === 0 && (
          <p className="text-sm text-gray-500">
            Schedule data will appear here.
          </p>
        )}
      </div>
    </div>
  );
}

function TeamHistory({ seasons }: { seasons: TeamHistorySeason[] }) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Franchise History</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Season</th>
              <th className="px-3 py-3 text-center">W</th>
              <th className="px-3 py-3 text-center">L</th>
              <th className="px-3 py-3 text-center">Win%</th>
              <th className="px-3 py-3 text-center">Playoffs</th>
            </tr>
          </thead>
          <tbody>
            {seasons.map((season, idx) => (
              <tr
                key={season.year}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <td className="px-4 py-3 font-medium">{season.year}</td>
                <td className="px-3 py-3 text-center">{season.wins}</td>
                <td className="px-3 py-3 text-center">{season.losses}</td>
                <td className="px-3 py-3 text-center">
                  {(season.win_pct * 100).toFixed(1)}%
                </td>
                <td className="px-3 py-3 text-center text-xs uppercase tracking-[0.2em]">
                  {season.made_playoffs ? season.playoff_round || "Yes" : "No"}
                </td>
              </tr>
            ))}
            {seasons.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No historical records available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default async function TeamPage({ params }: PageProps) {
  const { abbrev } = await params;

  let team: Team;
  try {
    team = await getTeam(abbrev);
  } catch {
    notFound();
  }

  const [rosterResult, statsResult, scheduleResult] = await Promise.allSettled([
    getTeamRoster(abbrev, currentSeasonYear),
    getTeamStats(abbrev, currentSeasonYear),
    getTeamSchedule(abbrev, currentSeasonYear),
  ]);
  const historyResult = await getTeamHistory(abbrev).catch(() => []);

  const roster = rosterResult.status === "fulfilled" ? rosterResult.value : [];
  const stats = statsResult.status === "fulfilled" ? statsResult.value : null;
  const schedule =
    scheduleResult.status === "fulfilled" ? scheduleResult.value : [];

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link href="/teams" className="hover:text-blue-600">
            Teams
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">
            {team.city} {team.name}
          </span>
        </nav>

        <TeamHeader team={team} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <RosterTable roster={roster} />
            <TeamHistory seasons={historyResult.slice(0, 10)} />
          </div>

          <div>
            <TeamStats stats={stats} />
            <RecentGames games={schedule} />
          </div>
        </div>
      </div>
    </div>
  );
}

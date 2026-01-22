import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getSeason,
  getSeasonLeaders,
  getSeasonSchedule,
  SeasonLeaders,
  SeasonScheduleGame,
} from "@/lib/api";

interface PageProps {
  params: Promise<{ year: string }>;
  searchParams: Promise<{ month?: string }>;
}

const LEADER_CATEGORIES = [
  { key: "points", label: "Points", unit: "PPG" },
  { key: "rebounds", label: "Rebounds", unit: "RPG" },
  { key: "assists", label: "Assists", unit: "APG" },
];

function ScheduleTable({ games }: { games: SeasonScheduleGame[] }) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Season Schedule</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-left">Visitor</th>
              <th className="px-4 py-3 text-left">Home</th>
              <th className="px-4 py-3 text-center">Score</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game, idx) => (
              <tr
                key={game.game_id}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <td className="px-4 py-3">
                  {new Date(game.date).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })}
                </td>
                <td className="px-4 py-3">{game.away_team_abbrev}</td>
                <td className="px-4 py-3">{game.home_team_abbrev}</td>
                <td className="px-4 py-3 text-center">
                  {game.home_score !== null && game.away_score !== null
                    ? `${game.away_score}-${game.home_score}`
                    : "TBD"}
                </td>
              </tr>
            ))}
            {games.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                  No schedule data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function LeadersCard({
  title,
  unit,
  leaders,
}: {
  title: string;
  unit: string;
  leaders: SeasonLeaders;
}) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-lg">
      <h3 className="mb-3 font-semibold text-gray-900">{title}</h3>
      <ol className="space-y-2">
        {leaders.leaders.map((leader) => (
          <li
            key={leader.player_slug}
            className="flex items-center justify-between text-sm"
          >
            <Link
              href={`/players/${leader.player_slug}`}
              className="truncate font-medium text-blue-600 hover:text-blue-800"
            >
              {leader.player_name}
            </Link>
            <span className="text-gray-500">
              {leader.value.toFixed(1)} {unit}
            </span>
          </li>
        ))}
        {leaders.leaders.length === 0 && (
          <li className="text-xs text-gray-400">No leader data.</li>
        )}
      </ol>
    </div>
  );
}

export default async function SeasonDetailPage({
  params,
  searchParams,
}: PageProps) {
  const { year } = await params;
  const { month } = await searchParams;
  const seasonYear = Number(year);
  const monthValue = month ? Number(month) : undefined;

  if (!seasonYear) {
    notFound();
  }

  let season;
  try {
    season = await getSeason(seasonYear);
  } catch {
    notFound();
  }

  const [schedule, leaders] = await Promise.all([
    getSeasonSchedule(seasonYear, monthValue),
    Promise.all(
      LEADER_CATEGORIES.map((category) =>
        getSeasonLeaders(seasonYear, {
          category: category.key,
          per_game: true,
          limit: 5,
        })
      )
    ),
  ]);

  return (
    <div className="mx-auto max-w-6xl space-y-10 py-12">
      <header className="text-center">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          {season.season_name}
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          {season.champion_team_name
            ? `${season.champion_team_name} were champions.`
            : "Season overview."}
        </p>
        <div className="mt-4 text-sm text-gray-400">
          <span>
            {season.start_date} - {season.end_date}
          </span>
        </div>
      </header>

      <section>
        <h2 className="mb-4 text-xl font-bold text-gray-900">League Leaders</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {leaders.map((leaderSet, index) => (
            <LeadersCard
              key={LEADER_CATEGORIES[index].key}
              title={LEADER_CATEGORIES[index].label}
              unit={LEADER_CATEGORIES[index].unit}
              leaders={leaderSet}
            />
          ))}
        </div>
      </section>

      <section>
        <form method="GET" className="mb-4 flex flex-wrap items-center gap-3">
          <label className="text-xs uppercase tracking-[0.3em] text-slate-500">
            Filter Month
          </label>
          <select
            name="month"
            defaultValue={monthValue ?? ""}
            className="rounded-full border border-slate-300 px-4 py-2 text-sm uppercase tracking-[0.2em]"
          >
            <option value="">All</option>
            {Array.from({ length: 12 }, (_, idx) => idx + 1).map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <button
            type="submit"
            className="rounded-full bg-slate-900 px-5 py-2 text-xs uppercase tracking-[0.3em] text-white"
          >
            Apply
          </button>
        </form>
        <ScheduleTable games={schedule.games} />
      </section>
    </div>
  );
}

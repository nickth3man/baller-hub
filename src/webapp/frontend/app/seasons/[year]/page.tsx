import { notFound } from "next/navigation";
import { getSeason, getSeasonLeaders, getSeasonSchedule } from "@/lib/api";
import { ScheduleTable } from "@/(components)/seasons/ScheduleTable";
import { LeadersCard } from "@/(components)/seasons/LeadersCard";

interface PageProps {
  params: Promise<{ year: string }>;
  searchParams: Promise<{ month?: string }>;
}

const LEADER_CATEGORIES = [
  { key: "points", label: "Points", unit: "PPG" },
  { key: "rebounds", label: "Rebounds", unit: "RPG" },
  { key: "assists", label: "Assists", unit: "APG" },
];

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

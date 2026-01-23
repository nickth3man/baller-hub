import Link from "next/link";
import { getSeasonLeaders, getSeasons } from "@/lib/api";
import { SeasonLeaders } from "@/types";

const CATEGORIES = [
  { key: "points", label: "Points", unit: "PPG" },
  { key: "rebounds", label: "Rebounds", unit: "RPG" },
  { key: "assists", label: "Assists", unit: "APG" },
  { key: "steals", label: "Steals", unit: "SPG" },
  { key: "blocks", label: "Blocks", unit: "BPG" },
];

export async function LeagueLeaders() {
  const seasons = await getSeasons();
  const current = seasons.find((season) => season.is_active) || seasons[0];

  if (!current) {
    return (
      <div className="rounded-lg bg-white p-6 text-sm text-gray-500 shadow">
        Season data unavailable.
      </div>
    );
  }

  const leaders = await Promise.all(
    CATEGORIES.map((category) =>
      getSeasonLeaders(current.year, {
        category: category.key,
        per_game: true,
        limit: 3,
      })
    )
  );

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-5">
      {leaders.map((leaderSet, index) => (
        <LeaderCategory
          key={CATEGORIES[index].key}
          title={CATEGORIES[index].label}
          unit={CATEGORIES[index].unit}
          leaders={leaderSet}
        />
      ))}
    </div>
  );
}

function LeaderCategory({
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
        {leaders.leaders.map((leader, i) => (
          <li key={leader.player_slug} className="flex items-start">
            <span className="mr-2 text-sm text-gray-400">{i + 1}.</span>
            <div className="min-w-0 flex-1">
              <Link
                href={`/players/${leader.player_slug}`}
                className="block truncate text-sm font-medium text-gray-900 hover:text-primary-600"
              >
                {leader.player_name}
              </Link>
              <span className="text-sm font-semibold text-primary-600">
                {leader.value.toFixed(1)} {unit}
              </span>
            </div>
          </li>
        ))}
        {leaders.leaders.length === 0 && (
          <li className="text-xs text-gray-400">No data available.</li>
        )}
      </ol>
    </div>
  );
}

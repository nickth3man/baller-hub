import { notFound } from "next/navigation";
import Link from "next/link";
import { getPlayer, getPlayerCareerStats } from "@/lib/api";
import { Player } from "@/types";
import { PlayerBio } from "@/(components)/players/PlayerBio";
import { CareerStatsTable } from "@/(components)/players/CareerStatsTable";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function PlayerPage({ params }: PageProps) {
  const { slug } = await params;

  let player: Player;
  let careerStats;

  try {
    [player, careerStats] = await Promise.all([
      getPlayer(slug),
      getPlayerCareerStats(slug),
    ]);
  } catch {
    notFound();
  }

  const latestSeason = careerStats[0]?.season_year;
  const careerTotals = careerStats.reduce(
    (totals, season) => ({
      games: totals.games + season.games_played,
      points: totals.points + season.points,
      rebounds: totals.rebounds + season.rebounds,
      assists: totals.assists + season.assists,
    }),
    { games: 0, points: 0, rebounds: 0, assists: 0 }
  );
  const peakSeason = careerStats.reduce(
    (best, season) => {
      const gp = Math.max(season.games_played, 1);
      const ppg = season.points / gp;
      if (!best || ppg > best.ppg) {
        return { year: season.season_year, ppg };
      }
      return best;
    },
    null as { year: number; ppg: number } | null
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link href="/players" className="hover:text-blue-600">
            Players
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{player.full_name}</span>
        </nav>

        <PlayerBio player={player} />

        {careerStats.length > 0 && <CareerStatsTable stats={careerStats} />}

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-2xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              Recent Games
            </h2>
            {latestSeason ? (
              <Link
                href={`/players/${player.slug}/game-log/${latestSeason}`}
                className="text-sm font-medium text-blue-600 hover:text-blue-800"
              >
                View {latestSeason} game log
              </Link>
            ) : (
              <p className="text-sm text-gray-500">
                Game log data will appear here
              </p>
            )}
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              Career Highlights
            </h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Career Points
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {careerTotals.points.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Career Games
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {careerTotals.games.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Career Assists
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {careerTotals.assists.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Peak Season
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {peakSeason
                    ? `${peakSeason.year} (${peakSeason.ppg.toFixed(1)} PPG)`
                    : "-"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

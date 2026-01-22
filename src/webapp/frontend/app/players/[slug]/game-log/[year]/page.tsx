import Link from "next/link";
import { notFound } from "next/navigation";
import { getPlayerGameLog } from "@/lib/api";

interface PageProps {
  params: Promise<{ slug: string; year: string }>;
}

function formatMinutes(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export default async function PlayerGameLogPage({ params }: PageProps) {
  const { slug, year } = await params;
  const seasonYear = Number(year);

  if (!seasonYear) {
    notFound();
  }

  let gameLog;
  try {
    gameLog = await getPlayerGameLog(slug, seasonYear);
  } catch {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link href="/players" className="hover:text-blue-600">
            Players
          </Link>
          <span className="mx-2">/</span>
          <Link href={`/players/${slug}`} className="hover:text-blue-600">
            {gameLog.player_name}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{seasonYear} Game Log</span>
        </nav>

        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <div className="flex items-center justify-between bg-slate-900 px-6 py-4 text-white">
            <h1 className="text-lg font-semibold">
              {gameLog.player_name} - {seasonYear} Game Log
            </h1>
            <span className="text-xs uppercase tracking-widest text-blue-200">
              {gameLog.season_type}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-100 text-gray-700">
                <tr>
                  <th className="px-3 py-2 text-left">Date</th>
                  <th className="px-3 py-2 text-left">Opp</th>
                  <th className="px-3 py-2 text-center">Loc</th>
                  <th className="px-3 py-2 text-center">Res</th>
                  <th className="px-3 py-2 text-center">MIN</th>
                  <th className="px-3 py-2 text-center">PTS</th>
                  <th className="px-3 py-2 text-center">REB</th>
                  <th className="px-3 py-2 text-center">AST</th>
                  <th className="px-3 py-2 text-center">STL</th>
                  <th className="px-3 py-2 text-center">BLK</th>
                </tr>
              </thead>
              <tbody>
                {gameLog.games.map((game, idx) => (
                  <tr
                    key={game.game_id}
                    className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="px-3 py-2">
                      {new Date(game.game_date).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })}
                    </td>
                    <td className="px-3 py-2">{game.opponent_abbrev}</td>
                    <td className="px-3 py-2 text-center">{game.location}</td>
                    <td className="px-3 py-2 text-center">{game.outcome}</td>
                    <td className="px-3 py-2 text-center">
                      {formatMinutes(game.seconds_played)}
                    </td>
                    <td className="px-3 py-2 text-center font-medium">
                      {game.points}
                    </td>
                    <td className="px-3 py-2 text-center">{game.rebounds}</td>
                    <td className="px-3 py-2 text-center">{game.assists}</td>
                    <td className="px-3 py-2 text-center">{game.steals}</td>
                    <td className="px-3 py-2 text-center">{game.blocks}</td>
                  </tr>
                ))}
                {gameLog.games.length === 0 && (
                  <tr>
                    <td
                      colSpan={10}
                      className="px-3 py-6 text-center text-gray-500"
                    >
                      No game log entries found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

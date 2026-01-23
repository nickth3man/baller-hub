import { notFound } from "next/navigation";
import Link from "next/link";
import { getBoxScore } from "@/lib/api";
import { BoxScoreResponse } from "@/types";
import { GameHeader } from "@/(components)/games/GameHeader";
import { PlayerStatsTable } from "@/(components)/games/PlayerStatsTable";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function GamePage({ params }: PageProps) {
  const { id } = await params;
  const gameId = parseInt(id, 10);

  if (isNaN(gameId)) {
    notFound();
  }

  let boxScore: BoxScoreResponse;

  try {
    boxScore = await getBoxScore(gameId);
  } catch {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link href="/games" className="hover:text-blue-600">
            Games
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">Box Score</span>
        </nav>

        <GameHeader boxScore={boxScore} />

        <div className="grid grid-cols-1 gap-6">
          <PlayerStatsTable
            players={boxScore.away_team.players}
            teamLabel={
              boxScore.away_team.team_name ||
              boxScore.away_team.team_abbrev ||
              "Away"
            }
          />

          <PlayerStatsTable
            players={boxScore.home_team.players}
            teamLabel={
              boxScore.home_team.team_name ||
              boxScore.home_team.team_abbrev ||
              "Home"
            }
          />
        </div>
      </div>
    </div>
  );
}

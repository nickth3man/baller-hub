"use client";

export function TodaysGames() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Today's Games</h2>
      <div className="space-y-4">
        <GameCard
          awayTeam={{ abbrev: "LAL", name: "Lakers", score: 112 }}
          homeTeam={{ abbrev: "BOS", name: "Celtics", score: 118 }}
          status="Final"
          time="7:00 PM ET"
        />
        <GameCard
          awayTeam={{ abbrev: "GSW", name: "Warriors", score: 105 }}
          homeTeam={{ abbrev: "PHX", name: "Suns", score: 98 }}
          status="Final"
          time="9:30 PM ET"
        />
        <GameCard
          awayTeam={{ abbrev: "MIA", name: "Heat" }}
          homeTeam={{ abbrev: "NYK", name: "Knicks" }}
          status="10:00 PM ET"
        />
      </div>
    </div>
  );
}

interface Team {
  abbrev: string;
  name: string;
  score?: number;
}

interface GameCardProps {
  awayTeam: Team;
  homeTeam: Team;
  status: string;
  time?: string;
}

function GameCard({ awayTeam, homeTeam, status }: GameCardProps) {
  const isFinal = status === "Final";

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <span className={`text-xs font-medium ${isFinal ? "text-gray-500" : "text-green-600"}`}>
          {status}
        </span>
      </div>
      <div className="space-y-2">
        <TeamRow team={awayTeam} isWinner={isFinal && (awayTeam.score ?? 0) > (homeTeam.score ?? 0)} />
        <TeamRow team={homeTeam} isWinner={isFinal && (homeTeam.score ?? 0) > (awayTeam.score ?? 0)} />
      </div>
    </div>
  );
}

function TeamRow({ team, isWinner }: { team: Team; isWinner: boolean }) {
  return (
    <div className="flex justify-between items-center">
      <div className="flex items-center space-x-2">
        <span className={`font-medium ${isWinner ? "text-gray-900" : "text-gray-600"}`}>
          {team.abbrev}
        </span>
        <span className="text-gray-500 text-sm">{team.name}</span>
      </div>
      {team.score !== undefined && (
        <span className={`font-bold text-lg ${isWinner ? "text-gray-900" : "text-gray-500"}`}>
          {team.score}
        </span>
      )}
    </div>
  );
}

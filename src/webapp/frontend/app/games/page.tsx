import Link from 'next/link';
import { getGames } from '@/lib/api';

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

export default async function GamesPage() {
  const today = new Date();
  const endDate = today.toISOString().slice(0, 10);
  const startDate = new Date(today);
  startDate.setDate(today.getDate() - 7);

  const games = await getGames({
    startDate: startDate.toISOString().slice(0, 10),
    endDate,
    per_page: 200,
  });

  const gamesByDate = games.items.reduce<Record<string, typeof games.items>>(
    (acc, game) => {
      acc[game.date] = acc[game.date] || [];
      acc[game.date].push(game);
      return acc;
    },
    {}
  );

  const sortedDates = Object.keys(gamesByDate).sort().reverse();

  return (
    <div className="max-w-6xl mx-auto py-12 space-y-8">
      <header className="text-center">
        <h1 className="text-5xl font-black text-gray-900">Games</h1>
        <p className="mt-3 text-lg text-gray-500">Recent results and matchups.</p>
      </header>

      <div className="space-y-6">
        {sortedDates.map((date) => (
          <div key={date} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 bg-gray-900 text-white">
              <h2 className="text-base font-semibold">{formatDate(date)}</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {gamesByDate[date].map((game) => {
                const awayLabel = game.away_team_abbrev || game.away_team_id;
                const homeLabel = game.home_team_abbrev || game.home_team_id;
                const score =
                  game.home_score !== null && game.away_score !== null
                    ? `${game.away_score}-${game.home_score}`
                    : 'TBD';
                return (
                  <Link
                    key={game.game_id}
                    href={`/games/${game.game_id}`}
                    className="flex items-center justify-between px-6 py-4 text-sm hover:bg-gray-50"
                  >
                    <div className="font-semibold text-gray-900">
                      {awayLabel} @ {homeLabel}
                    </div>
                    <div className="text-gray-500">{score}</div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
        {sortedDates.length === 0 && (
          <div className="text-center text-gray-500 text-sm">
            No games available in this range.
          </div>
        )}
      </div>
    </div>
  );
}

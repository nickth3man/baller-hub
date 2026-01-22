import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getPlayer, getPlayerCareerStats, Player, PlayerSeasonStats } from '@/lib/api';

interface PageProps {
  params: Promise<{ slug: string }>;
}

function formatHeight(inches: number | null): string {
  if (!inches) return '-';
  const feet = Math.floor(inches / 12);
  const remainingInches = Math.round(inches % 12);
  return `${feet}'${remainingInches}"`;
}

function formatPercentage(made: number, attempted: number): string {
  if (attempted === 0) return '-';
  return ((made / attempted) * 100).toFixed(1);
}

function PlayerBio({ player }: { player: Player }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
      <div className="flex items-start gap-6">
        {/* Photo placeholder */}
        <div className="w-32 h-40 bg-gray-200 rounded-lg flex items-center justify-center text-gray-400">
          <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        </div>
        
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {player.full_name}
          </h1>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Position</span>
              <p className="font-medium">{player.position?.replace('_', ' ') || '-'}</p>
            </div>
            <div>
              <span className="text-gray-500">Height</span>
              <p className="font-medium">{formatHeight(player.height_inches)}</p>
            </div>
            <div>
              <span className="text-gray-500">Weight</span>
              <p className="font-medium">{player.weight_lbs ? `${player.weight_lbs} lbs` : '-'}</p>
            </div>
            <div>
              <span className="text-gray-500">Born</span>
              <p className="font-medium">
                {player.birth_date || '-'}
                {player.birth_place_city && ` in ${player.birth_place_city}`}
              </p>
            </div>
            <div>
              <span className="text-gray-500">College</span>
              <p className="font-medium">{player.college || '-'}</p>
            </div>
            <div>
              <span className="text-gray-500">High School</span>
              <p className="font-medium">{player.high_school || '-'}</p>
            </div>
            <div>
              <span className="text-gray-500">Draft</span>
              <p className="font-medium">
                {player.draft_year ? `${player.draft_year} (Pick ${player.draft_pick})` : 'Undrafted'}
              </p>
            </div>
            <div>
              <span className="text-gray-500">Experience</span>
              <p className="font-medium">
                {player.debut_year && player.final_year 
                  ? `${player.debut_year}-${player.is_active ? 'Present' : player.final_year}`
                  : '-'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CareerStatsTable({ stats }: { stats: PlayerSeasonStats[] }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden mb-6">
      <div className="px-6 py-4 bg-slate-900 text-white">
        <h2 className="text-lg font-semibold">Career Statistics</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-3 py-2 text-left">Season</th>
              <th className="px-3 py-2 text-center">G</th>
              <th className="px-3 py-2 text-center">GS</th>
              <th className="px-3 py-2 text-center">MPG</th>
              <th className="px-3 py-2 text-center">PPG</th>
              <th className="px-3 py-2 text-center">RPG</th>
              <th className="px-3 py-2 text-center">APG</th>
              <th className="px-3 py-2 text-center">SPG</th>
              <th className="px-3 py-2 text-center">BPG</th>
              <th className="px-3 py-2 text-center">FG%</th>
              <th className="px-3 py-2 text-center">3P%</th>
              <th className="px-3 py-2 text-center">FT%</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((season, idx) => {
              const gp = season.games_played || 1;
              return (
                <tr 
                  key={`${season.season_id}-${season.season_type}`}
                  className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  <td className="px-3 py-2 font-medium">{season.season_year}</td>
                  <td className="px-3 py-2 text-center">{season.games_played}</td>
                  <td className="px-3 py-2 text-center">{season.games_started}</td>
                  <td className="px-3 py-2 text-center">{(season.minutes_played / gp).toFixed(1)}</td>
                  <td className="px-3 py-2 text-center font-medium">{(season.points / gp).toFixed(1)}</td>
                  <td className="px-3 py-2 text-center">{(season.rebounds / gp).toFixed(1)}</td>
                  <td className="px-3 py-2 text-center">{(season.assists / gp).toFixed(1)}</td>
                  <td className="px-3 py-2 text-center">{(season.steals / gp).toFixed(1)}</td>
                  <td className="px-3 py-2 text-center">{(season.blocks / gp).toFixed(1)}</td>
                  <td className="px-3 py-2 text-center">{formatPercentage(season.fg_made, season.fg_attempted)}</td>
                  <td className="px-3 py-2 text-center">{formatPercentage(season.fg3_made, season.fg3_attempted)}</td>
                  <td className="px-3 py-2 text-center">{formatPercentage(season.ft_made, season.ft_attempted)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default async function PlayerPage({ params }: PageProps) {
  const { slug } = await params;
  
  let player: Player;
  let careerStats: PlayerSeasonStats[];
  
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
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">Home</Link>
          <span className="mx-2">/</span>
          <Link href="/players" className="hover:text-blue-600">Players</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{player.full_name}</span>
        </nav>

        <PlayerBio player={player} />
        
        {careerStats.length > 0 && (
          <CareerStatsTable stats={careerStats} />
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Games</h2>
            {latestSeason ? (
              <Link
                href={`/players/${player.slug}/game-log/${latestSeason}`}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View {latestSeason} game log
              </Link>
            ) : (
              <p className="text-gray-500 text-sm">Game log data will appear here</p>
            )}
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Career Highlights</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Career Points</p>
                <p className="text-2xl font-bold text-slate-900">
                  {careerTotals.points.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Career Games</p>
                <p className="text-2xl font-bold text-slate-900">
                  {careerTotals.games.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Career Assists</p>
                <p className="text-2xl font-bold text-slate-900">
                  {careerTotals.assists.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-orange-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Peak Season</p>
                <p className="text-2xl font-bold text-slate-900">
                  {peakSeason ? `${peakSeason.year} (${peakSeason.ppg.toFixed(1)} PPG)` : '-'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

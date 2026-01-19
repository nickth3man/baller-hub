import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getBoxScore, BoxScoreResponse, PlayerBoxScore } from '@/lib/api';

interface PageProps {
  params: Promise<{ id: string }>;
}

function formatMinutes(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function GameHeader({ boxScore }: { boxScore: BoxScoreResponse }) {
  const { game, home_team, away_team } = boxScore;
  const isFinal = game.is_final;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="text-center text-sm text-gray-500 mb-4">
        {new Date(game.date).toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })}
        {game.arena && ` • ${game.arena}`}
      </div>

      <div className="flex items-center justify-center gap-8">
        {/* Away Team */}
        <div className="text-center flex-1">
          <div className="w-20 h-20 mx-auto bg-gray-200 rounded-lg flex items-center justify-center text-2xl font-bold text-gray-600 mb-2">
            {away_team.team_id}
          </div>
          <p className="text-lg font-semibold text-gray-900">Away</p>
          <p className={`text-4xl font-bold ${!isFinal ? 'text-gray-400' : away_team.score! > home_team.score! ? 'text-green-600' : 'text-gray-900'}`}>
            {away_team.score ?? '-'}
          </p>
        </div>

        {/* VS / Final */}
        <div className="text-center">
          <p className={`text-lg font-bold ${isFinal ? 'text-red-600' : 'text-gray-400'}`}>
            {isFinal ? 'FINAL' : 'VS'}
          </p>
        </div>

        {/* Home Team */}
        <div className="text-center flex-1">
          <div className="w-20 h-20 mx-auto bg-gray-200 rounded-lg flex items-center justify-center text-2xl font-bold text-gray-600 mb-2">
            {home_team.team_id}
          </div>
          <p className="text-lg font-semibold text-gray-900">Home</p>
          <p className={`text-4xl font-bold ${!isFinal ? 'text-gray-400' : home_team.score! > away_team.score! ? 'text-green-600' : 'text-gray-900'}`}>
            {home_team.score ?? '-'}
          </p>
        </div>
      </div>

      {/* Quarter Scores */}
      {(home_team.box_score?.quarter_scores || away_team.box_score?.quarter_scores) && (
        <div className="mt-6 flex justify-center">
          <table className="text-sm">
            <thead>
              <tr className="text-gray-500">
                <th className="px-4 py-1"></th>
                <th className="px-3 py-1 text-center">Q1</th>
                <th className="px-3 py-1 text-center">Q2</th>
                <th className="px-3 py-1 text-center">Q3</th>
                <th className="px-3 py-1 text-center">Q4</th>
                <th className="px-3 py-1 text-center font-semibold">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="px-4 py-1 font-medium">Away</td>
                <td className="px-3 py-1 text-center">{away_team.box_score?.quarter_scores?.['1'] ?? '-'}</td>
                <td className="px-3 py-1 text-center">{away_team.box_score?.quarter_scores?.['2'] ?? '-'}</td>
                <td className="px-3 py-1 text-center">{away_team.box_score?.quarter_scores?.['3'] ?? '-'}</td>
                <td className="px-3 py-1 text-center">{away_team.box_score?.quarter_scores?.['4'] ?? '-'}</td>
                <td className="px-3 py-1 text-center font-bold">{away_team.score ?? '-'}</td>
              </tr>
              <tr>
                <td className="px-4 py-1 font-medium">Home</td>
                <td className="px-3 py-1 text-center">{home_team.box_score?.quarter_scores?.['1'] ?? '-'}</td>
                <td className="px-3 py-1 text-center">{home_team.box_score?.quarter_scores?.['2'] ?? '-'}</td>
                <td className="px-3 py-1 text-center">{home_team.box_score?.quarter_scores?.['3'] ?? '-'}</td>
                <td className="px-3 py-1 text-center">{home_team.box_score?.quarter_scores?.['4'] ?? '-'}</td>
                <td className="px-3 py-1 text-center font-bold">{home_team.score ?? '-'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function PlayerStatsTable({ players, teamLabel }: { players: PlayerBoxScore[]; teamLabel: string }) {
  const starters = players.filter(p => p.is_starter);
  const bench = players.filter(p => !p.is_starter);

  const renderPlayerRow = (player: PlayerBoxScore, idx: number) => (
    <tr 
      key={player.player_id}
      className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
    >
      <td className="px-3 py-2">
        <Link 
          href={`/players/${player.slug}`}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          {player.name}
        </Link>
        <span className="ml-2 text-xs text-gray-500">{player.position?.split('_').map(w => w[0]).join('') || ''}</span>
      </td>
      <td className="px-2 py-2 text-center text-gray-600">{formatMinutes(player.minutes)}</td>
      <td className="px-2 py-2 text-center font-semibold">{player.points}</td>
      <td className="px-2 py-2 text-center">{player.rebounds}</td>
      <td className="px-2 py-2 text-center">{player.assists}</td>
      <td className="px-2 py-2 text-center">{player.steals}</td>
      <td className="px-2 py-2 text-center">{player.blocks}</td>
      <td className="px-2 py-2 text-center">{player.fg_made}-{player.fg_attempted}</td>
      <td className="px-2 py-2 text-center">{player.fg3_made}-{player.fg3_attempted}</td>
      <td className="px-2 py-2 text-center">{player.ft_made}-{player.ft_attempted}</td>
      <td className="px-2 py-2 text-center">{player.turnovers}</td>
      <td className="px-2 py-2 text-center">{player.personal_fouls}</td>
      <td className="px-2 py-2 text-center">{player.plus_minus !== null ? (player.plus_minus > 0 ? `+${player.plus_minus}` : player.plus_minus) : '-'}</td>
    </tr>
  );

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
      <div className="px-6 py-4 bg-blue-900 text-white">
        <h2 className="text-lg font-semibold">{teamLabel}</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-3 py-2 text-left min-w-[150px]">Player</th>
              <th className="px-2 py-2 text-center">MIN</th>
              <th className="px-2 py-2 text-center">PTS</th>
              <th className="px-2 py-2 text-center">REB</th>
              <th className="px-2 py-2 text-center">AST</th>
              <th className="px-2 py-2 text-center">STL</th>
              <th className="px-2 py-2 text-center">BLK</th>
              <th className="px-2 py-2 text-center">FG</th>
              <th className="px-2 py-2 text-center">3PT</th>
              <th className="px-2 py-2 text-center">FT</th>
              <th className="px-2 py-2 text-center">TO</th>
              <th className="px-2 py-2 text-center">PF</th>
              <th className="px-2 py-2 text-center">+/-</th>
            </tr>
          </thead>
          <tbody>
            {/* Starters */}
            {starters.length > 0 && (
              <>
                <tr className="bg-gray-200">
                  <td colSpan={13} className="px-3 py-1 text-xs font-semibold text-gray-600 uppercase">
                    Starters
                  </td>
                </tr>
                {starters.map(renderPlayerRow)}
              </>
            )}
            
            {/* Bench */}
            {bench.length > 0 && (
              <>
                <tr className="bg-gray-200">
                  <td colSpan={13} className="px-3 py-1 text-xs font-semibold text-gray-600 uppercase">
                    Bench
                  </td>
                </tr>
                {bench.map(renderPlayerRow)}
              </>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
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
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">Home</Link>
          <span className="mx-2">/</span>
          <Link href="/games" className="hover:text-blue-600">Games</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">Box Score</span>
        </nav>

        <GameHeader boxScore={boxScore} />
        
        <div className="grid grid-cols-1 gap-6">
          <PlayerStatsTable 
            players={boxScore.away_team.players} 
            teamLabel={`Away Team (${boxScore.away_team.team_id})`}
          />
          
          <PlayerStatsTable 
            players={boxScore.home_team.players} 
            teamLabel={`Home Team (${boxScore.home_team.team_id})`}
          />
        </div>
      </div>
    </div>
  );
}

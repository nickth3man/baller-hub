import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getTeam, getTeamRoster, Team, RosterPlayer } from '@/lib/api';

interface PageProps {
  params: Promise<{ abbrev: string }>;
}

const currentYear = new Date().getFullYear();

function TeamHeader({ team }: { team: Team }) {
  return (
    <div className="bg-blue-900 text-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center gap-6">
        {/* Logo placeholder */}
        <div className="w-24 h-24 bg-blue-800 rounded-lg flex items-center justify-center text-4xl font-bold">
          {team.abbreviation}
        </div>
        
        <div className="flex-1">
          <h1 className="text-3xl font-bold mb-1">
            {team.city} {team.name}
          </h1>
          <p className="text-blue-200">
            {team.arena && `${team.arena}`}
            {team.arena_capacity && ` • Capacity: ${team.arena_capacity.toLocaleString()}`}
          </p>
          <p className="text-blue-200 text-sm mt-1">
            Est. {team.founded_year}
            {team.franchise && ` • ${team.franchise.name} Franchise`}
          </p>
        </div>
      </div>
    </div>
  );
}

function RosterTable({ roster, teamAbbrev }: { roster: RosterPlayer[]; teamAbbrev: string }) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
      <div className="px-6 py-4 bg-gray-800 text-white flex justify-between items-center">
        <h2 className="text-lg font-semibold">Current Roster</h2>
        <span className="text-sm text-gray-300">{currentYear} Season</span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Player</th>
              <th className="px-3 py-3 text-center">Pos</th>
              <th className="px-3 py-3 text-center">GP</th>
              <th className="px-3 py-3 text-center">GS</th>
              <th className="px-3 py-3 text-center">PPG</th>
            </tr>
          </thead>
          <tbody>
            {roster.map((player, idx) => (
              <tr 
                key={player.player_id}
                className={`${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}
              >
                <td className="px-4 py-3">
                  <Link 
                    href={`/players/${player.slug}`}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {player.name}
                  </Link>
                </td>
                <td className="px-3 py-3 text-center text-gray-600">
                  {player.position?.replace('_', ' ').split(' ').map(w => w[0]).join('') || '-'}
                </td>
                <td className="px-3 py-3 text-center">{player.games_played}</td>
                <td className="px-3 py-3 text-center">{player.games_started}</td>
                <td className="px-3 py-3 text-center font-medium">{player.ppg?.toFixed(1) || '-'}</td>
              </tr>
            ))}
            {roster.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No roster data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TeamStats() {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Season Stats</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">-</p>
          <p className="text-sm text-gray-500">Wins</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">-</p>
          <p className="text-sm text-gray-500">Losses</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">-</p>
          <p className="text-sm text-gray-500">PPG</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">-</p>
          <p className="text-sm text-gray-500">Opp PPG</p>
        </div>
      </div>
    </div>
  );
}

export default async function TeamPage({ params }: PageProps) {
  const { abbrev } = await params;
  
  let team: Team;
  let roster: RosterPlayer[];
  
  try {
    [team, roster] = await Promise.all([
      getTeam(abbrev),
      getTeamRoster(abbrev, currentYear),
    ]);
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
          <Link href="/teams" className="hover:text-blue-600">Teams</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{team.city} {team.name}</span>
        </nav>

        <TeamHeader team={team} />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RosterTable roster={roster} teamAbbrev={abbrev} />
          </div>
          
          <div>
            <TeamStats />
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Games</h2>
              <p className="text-gray-500 text-sm">Schedule data will appear here</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

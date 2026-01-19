import { Metadata } from 'next';
import Link from 'next/link';
import { getTeams, Team } from '@/lib/api';

export const metadata: Metadata = {
  title: 'Teams | Basketball Reference',
  description: 'View all 30 NBA teams by conference and division.',
};

const EASTERN_CONFERENCE_ABBREVS = [
  'ATL', 'BOS', 'BRK', 'CHI', 'CHO', 'CLE', 'DET', 'IND', 'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS'
];

const WESTERN_CONFERENCE_ABBREVS = [
  'DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN', 'NOP', 'OKC', 'PHO', 'POR', 'SAC', 'SAS', 'UTA'
];

function TeamCard({ team }: { team: Team }) {
  return (
    <Link 
      href={`/teams/${team.abbreviation}`}
      className="group relative bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-xl hover:border-blue-900/30 transition-all duration-300 overflow-hidden"
    >
      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
        <span className="text-6xl font-black italic">{team.abbreviation}</span>
      </div>
      
      <div className="relative z-10">
        <h3 className="text-xl font-black text-gray-900 group-hover:text-blue-900 transition-colors">
          {team.name}
        </h3>
        <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mt-1">
          {team.city}
        </p>
        
        <div className="mt-6 flex flex-col gap-1 text-xs text-gray-500 font-medium">
          <div className="flex justify-between">
            <span>Arena</span>
            <span className="text-gray-900 font-bold">{team.arena || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span>Founded</span>
            <span className="text-gray-900 font-bold">{team.founded_year || '-'}</span>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-50 flex items-center text-blue-900 font-black text-xs uppercase tracking-tighter">
        View Team Profile
        <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </div>
    </Link>
  );
}

export default async function TeamsPage() {
  const allTeams = await getTeams();
  
  const eastTeams = allTeams
    .filter(t => t.is_active && EASTERN_CONFERENCE_ABBREVS.includes(t.abbreviation))
    .sort((a, b) => a.name.localeCompare(b.name));
    
  const westTeams = allTeams
    .filter(t => t.is_active && WESTERN_CONFERENCE_ABBREVS.includes(t.abbreviation))
    .sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="space-y-12 animate-in slide-in-from-bottom-4 duration-700">
      <div className="max-w-3xl">
        <h1 className="text-5xl font-black text-gray-900 tracking-tighter">
          The Associations
        </h1>
        <p className="mt-4 text-xl text-gray-500 font-medium leading-relaxed">
          The premier professional basketball league in North America. Thirty franchises, one Larry O&apos;Brien Trophy.
        </p>
      </div>

      <section>
        <div className="flex items-center gap-4 mb-8">
          <div className="h-px flex-1 bg-gradient-to-r from-blue-900 to-transparent"></div>
          <h2 className="text-2xl font-black text-blue-900 uppercase tracking-[0.2em]">Eastern Conference</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {eastTeams.map(team => (
            <TeamCard key={team.team_id} team={team} />
          ))}
        </div>
      </section>

      <section>
        <div className="flex items-center gap-4 mb-8">
          <div className="h-px flex-1 bg-gradient-to-r from-red-600 to-transparent"></div>
          <h2 className="text-2xl font-black text-red-600 uppercase tracking-[0.2em]">Western Conference</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {westTeams.map(team => (
            <TeamCard key={team.team_id} team={team} />
          ))}
        </div>
      </section>
      
      {allTeams.length === 0 && (
        <div className="py-20 text-center bg-white rounded-xl border border-dashed border-gray-300">
          <p className="text-gray-400 font-medium">Loading league data...</p>
        </div>
      )}
    </div>
  );
}

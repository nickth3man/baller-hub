import { Metadata } from 'next';
import Link from 'next/link';
import { getSeasons } from '@/lib/api';

export const metadata: Metadata = {
  title: 'Seasons | Basketball Reference',
  description: 'Historical NBA seasons and championship history.',
};

export default async function SeasonsPage() {
  const seasons = await getSeasons();
  
  // Filter for 2020-present and sort descending
  const recentSeasons = seasons
    .filter(s => s.year >= 2020)
    .sort((a, b) => b.year - a.year);

  return (
    <div className="max-w-4xl mx-auto py-12 animate-in fade-in slide-in-from-top-4 duration-1000">
      <header className="mb-16 text-center">
        <h1 className="text-7xl font-display uppercase tracking-[0.2em] text-gray-900 mb-4">
          Seasons
        </h1>
        <div className="h-1.5 w-24 bg-blue-900 mx-auto rounded-full"></div>
        <p className="mt-6 text-xl text-gray-500 font-medium">
          A definitive timeline of the modern era.
        </p>
      </header>

      <div className="space-y-4">
        {recentSeasons.map((season) => (
          <Link
            key={season.season_id}
            href={`/seasons/${season.year}`}
            className="group block bg-white border border-gray-200 rounded-2xl p-8 hover:border-blue-900 hover:shadow-2xl transition-all duration-500 relative overflow-hidden"
          >
            {/* Background Year Accent */}
            <div className="absolute -right-4 -bottom-8 text-9xl font-black text-gray-50 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity pointer-events-none uppercase">
              {season.year}
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 relative z-10">
              <div className="flex items-center gap-6">
                <span className="text-5xl font-black text-blue-900 tabular-nums tracking-tighter">
                  {season.year}
                </span>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 group-hover:text-blue-900 transition-colors">
                    {season.season_name}
                  </h2>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`w-2 h-2 rounded-full ${season.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></span>
                    <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
                      {season.is_active ? 'Live Season' : 'Finalized'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col items-start sm:items-end">
                <span className="text-xs font-bold uppercase tracking-[0.2em] text-gray-400 mb-1">Champion</span>
                <span className="text-xl font-black text-gray-900 italic">
                  {season.champion || (season.is_active ? 'TBD' : 'N/A')}
                </span>
              </div>
            </div>
            
            <div className="mt-8 flex items-center justify-end text-sm font-black text-blue-900 uppercase tracking-widest opacity-0 group-hover:opacity-100 translate-x-4 group-hover:translate-x-0 transition-all">
              Season Analytics
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </Link>
        ))}

        {recentSeasons.length === 0 && (
          <div className="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
            <p className="text-gray-400 font-bold text-xl uppercase tracking-widest">No seasons archived yet</p>
          </div>
        )}
      </div>
    </div>
  );
}

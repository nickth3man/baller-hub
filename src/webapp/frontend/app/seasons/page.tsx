import { Metadata } from "next";
import Link from "next/link";
import { getSeasons } from "@/lib/api";

export const metadata: Metadata = {
  title: "Seasons | Basketball Reference",
  description: "Historical NBA seasons and championship history.",
};

export default async function SeasonsPage() {
  const seasons = await getSeasons();

  // Filter for 2020-present and sort descending
  const recentSeasons = seasons
    .filter((s) => s.year >= 2020)
    .sort((a, b) => b.year - a.year);

  return (
    <div className="animate-in fade-in slide-in-from-top-4 mx-auto max-w-4xl py-12 duration-1000">
      <header className="mb-16 text-center">
        <h1 className="mb-4 font-display text-7xl uppercase tracking-[0.2em] text-gray-900">
          Seasons
        </h1>
        <div className="mx-auto h-1.5 w-24 rounded-full bg-blue-900"></div>
        <p className="mt-6 text-xl font-medium text-gray-500">
          A definitive timeline of the modern era.
        </p>
      </header>

      <div className="space-y-4">
        {recentSeasons.map((season) => (
          <Link
            key={season.season_id}
            href={`/seasons/${season.year}`}
            className="group relative block overflow-hidden rounded-2xl border border-gray-200 bg-white p-8 transition-all duration-500 hover:border-blue-900 hover:shadow-2xl"
          >
            {/* Background Year Accent */}
            <div className="pointer-events-none absolute -bottom-8 -right-4 text-9xl font-black uppercase text-gray-50 opacity-[0.03] transition-opacity group-hover:opacity-[0.08]">
              {season.year}
            </div>

            <div className="relative z-10 flex flex-col justify-between gap-6 sm:flex-row sm:items-center">
              <div className="flex items-center gap-6">
                <span className="text-5xl font-black tabular-nums tracking-tighter text-blue-900">
                  {season.year}
                </span>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 transition-colors group-hover:text-blue-900">
                    {season.season_name}
                  </h2>
                  <div className="mt-1 flex items-center gap-2">
                    <span
                      className={`h-2 w-2 rounded-full ${season.is_active ? "animate-pulse bg-green-500" : "bg-gray-300"}`}
                    ></span>
                    <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
                      {season.is_active ? "Live Season" : "Finalized"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col items-start sm:items-end">
                <span className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-gray-400">
                  Champion
                </span>
                <span className="text-xl font-black italic text-gray-900">
                  {season.champion || (season.is_active ? "TBD" : "N/A")}
                </span>
              </div>
            </div>

            <div className="mt-8 flex translate-x-4 items-center justify-end text-sm font-black uppercase tracking-widest text-blue-900 opacity-0 transition-all group-hover:translate-x-0 group-hover:opacity-100">
              Season Analytics
              <svg
                className="ml-2 h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={3}
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </div>
          </Link>
        ))}

        {recentSeasons.length === 0 && (
          <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50 py-20 text-center">
            <p className="text-xl font-bold uppercase tracking-widest text-gray-400">
              No seasons archived yet
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

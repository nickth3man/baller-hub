import { Metadata } from "next";
import Link from "next/link";
import { getTeams, Team } from "@/lib/api";

export const metadata: Metadata = {
  title: "Teams | Basketball Reference",
  description: "View all 30 NBA teams by conference and division.",
};

const EASTERN_CONFERENCE_ABBREVS = [
  "ATL",
  "BOS",
  "BRK",
  "CHI",
  "CHO",
  "CLE",
  "DET",
  "IND",
  "MIA",
  "MIL",
  "NYK",
  "ORL",
  "PHI",
  "TOR",
  "WAS",
];

const WESTERN_CONFERENCE_ABBREVS = [
  "DAL",
  "DEN",
  "GSW",
  "HOU",
  "LAC",
  "LAL",
  "MEM",
  "MIN",
  "NOP",
  "OKC",
  "PHO",
  "POR",
  "SAC",
  "SAS",
  "UTA",
];

function TeamCard({ team }: { team: Team }) {
  return (
    <Link
      href={`/teams/${team.abbreviation}`}
      className="group relative overflow-hidden rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-300 hover:border-blue-900/30 hover:shadow-xl"
    >
      <div className="absolute right-0 top-0 p-4 opacity-5 transition-opacity group-hover:opacity-10">
        <span className="text-6xl font-black italic">{team.abbreviation}</span>
      </div>

      <div className="relative z-10">
        <h3 className="text-xl font-black text-gray-900 transition-colors group-hover:text-blue-900">
          {team.name}
        </h3>
        <p className="mt-1 text-sm font-bold uppercase tracking-widest text-gray-400">
          {team.city}
        </p>

        <div className="mt-6 flex flex-col gap-1 text-xs font-medium text-gray-500">
          <div className="flex justify-between">
            <span>Arena</span>
            <span className="font-bold text-gray-900">{team.arena || "-"}</span>
          </div>
          <div className="flex justify-between">
            <span>Founded</span>
            <span className="font-bold text-gray-900">
              {team.founded_year || "-"}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center border-t border-gray-50 pt-4 text-xs font-black uppercase tracking-tighter text-blue-900">
        View Team Profile
        <svg
          className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={3}
            d="M13 7l5 5m0 0l-5 5m5-5H6"
          />
        </svg>
      </div>
    </Link>
  );
}

export default async function TeamsPage() {
  const allTeams = await getTeams();

  const eastTeams = allTeams
    .filter(
      (t) => t.is_active && EASTERN_CONFERENCE_ABBREVS.includes(t.abbreviation)
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  const westTeams = allTeams
    .filter(
      (t) => t.is_active && WESTERN_CONFERENCE_ABBREVS.includes(t.abbreviation)
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="animate-in slide-in-from-bottom-4 space-y-12 duration-700">
      <div className="max-w-3xl">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          The Associations
        </h1>
        <p className="mt-4 text-xl font-medium leading-relaxed text-gray-500">
          The premier professional basketball league in North America. Thirty
          franchises, one Larry O&apos;Brien Trophy.
        </p>
      </div>

      <section>
        <div className="mb-8 flex items-center gap-4">
          <div className="h-px flex-1 bg-gradient-to-r from-blue-900 to-transparent"></div>
          <h2 className="text-2xl font-black uppercase tracking-[0.2em] text-blue-900">
            Eastern Conference
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {eastTeams.map((team) => (
            <TeamCard key={team.team_id} team={team} />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-8 flex items-center gap-4">
          <div className="h-px flex-1 bg-gradient-to-r from-red-600 to-transparent"></div>
          <h2 className="text-2xl font-black uppercase tracking-[0.2em] text-red-600">
            Western Conference
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {westTeams.map((team) => (
            <TeamCard key={team.team_id} team={team} />
          ))}
        </div>
      </section>

      {allTeams.length === 0 && (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white py-20 text-center">
          <p className="font-medium text-gray-400">Loading league data...</p>
        </div>
      )}
    </div>
  );
}

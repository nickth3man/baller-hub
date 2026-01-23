import { Team } from "@/types";

export function TeamHeader({ team }: { team: Team }) {
  return (
    <div className="mb-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-orange-600 p-6 text-white shadow-xl">
      <div className="flex flex-col items-start gap-6 md:flex-row md:items-center">
        <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-white/10 font-display text-4xl uppercase">
          {team.abbreviation}
        </div>

        <div className="flex-1">
          <h1 className="mb-1 font-display text-4xl uppercase tracking-[0.1em]">
            {team.city} {team.name}
          </h1>
          <p className="text-orange-100">
            {team.arena && `${team.arena}`}
            {team.arena_capacity &&
              ` - Capacity: ${team.arena_capacity.toLocaleString()}`}
          </p>
          <p className="mt-1 text-sm text-orange-200">
            Est. {team.founded_year}
            {team.franchise && ` - ${team.franchise.name} Franchise`}
          </p>
        </div>
      </div>
    </div>
  );
}

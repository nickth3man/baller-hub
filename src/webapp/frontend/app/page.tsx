import Link from "next/link";
import { TodaysGames } from "@/(components)/stats/TodaysGames";
import { LeagueLeaders } from "@/(components)/stats/LeagueLeaders";
import { StandingsPreview } from "@/(components)/stats/StandingsPreview";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-3xl bg-slate-900 p-8 text-white shadow-2xl">
        <div className="absolute -right-12 -top-16 h-52 w-52 rounded-full bg-orange-500/30 blur-2xl" />
        <div className="absolute -left-16 bottom-0 h-32 w-32 rounded-full bg-blue-500/30 blur-2xl" />
        <div className="relative z-10">
          <p className="text-xs uppercase tracking-[0.4em] text-orange-200">
            Basketball Intelligence
          </p>
          <h1 className="mt-4 font-display text-5xl uppercase tracking-[0.08em] md:text-6xl">
            Baller Hub
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-slate-200">
            A living archive of NBA history, box scores, and season trends.
            Follow today&apos;s games and jump into player and team timelines.
          </p>
          <div className="mt-6 flex flex-wrap gap-3 text-xs uppercase tracking-[0.25em]">
            <span className="rounded-full border border-white/30 px-4 py-2">
              Live Scoreboards
            </span>
            <span className="rounded-full border border-white/30 px-4 py-2">
              Season Leaders
            </span>
            <span className="rounded-full border border-white/30 px-4 py-2">
              Franchise DNA
            </span>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TodaysGames />
        </div>
        <div>
          <StandingsPreview />
        </div>
      </div>

      <section>
        <h2 className="mb-4 text-2xl font-bold text-gray-900">
          League Leaders
        </h2>
        <LeagueLeaders />
      </section>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <QuickLink
          href="/players"
          title="Players"
          description="Browse all players"
        />
        <QuickLink href="/teams" title="Teams" description="View team stats" />
        <QuickLink
          href="/seasons"
          title="Seasons"
          description="Historical data"
        />
        <QuickLink href="/search" title="Search" description="Find anything" />
      </section>
    </div>
  );
}

function QuickLink({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="group block rounded-2xl border border-gray-200 bg-white p-4 shadow transition-shadow hover:shadow-xl"
    >
      <h3 className="font-semibold text-gray-900 transition-colors group-hover:text-orange-600">
        {title}
      </h3>
      <p className="text-sm text-gray-500">{description}</p>
    </Link>
  );
}

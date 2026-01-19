import Link from "next/link";
import { TodaysGames } from "@/(components)/stats/TodaysGames";
import { LeagueLeaders } from "@/(components)/stats/LeagueLeaders";
import { StandingsPreview } from "@/(components)/stats/StandingsPreview";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Basketball Reference Clone
        </h1>
        <p className="text-gray-600 mb-6">
          Your local source for comprehensive NBA statistics and historical data.
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TodaysGames />
        </div>
        <div>
          <StandingsPreview />
        </div>
      </div>

      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          League Leaders
        </h2>
        <LeagueLeaders />
      </section>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickLink href="/players" title="Players" description="Browse all players" />
        <QuickLink href="/teams" title="Teams" description="View team stats" />
        <QuickLink href="/seasons" title="Seasons" description="Historical data" />
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
      className="block p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200"
    >
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-500">{description}</p>
    </Link>
  );
}

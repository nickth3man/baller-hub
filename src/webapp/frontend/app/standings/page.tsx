import {
  getSeasons,
  getStandings,
  StandingsTeam,
  StandingsView,
} from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/(components)/ui/Table";

function StandingsTable({
  title,
  teams,
}: {
  title: string;
  teams: StandingsTeam[];
}) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead className="w-[40%] text-gray-700">Team</TableHead>
              <TableHead className="text-center text-gray-700">W</TableHead>
              <TableHead className="text-center text-gray-700">L</TableHead>
              <TableHead className="text-center text-gray-700">PCT</TableHead>
              <TableHead className="text-center text-gray-700">GB</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {teams.map((team, idx) => (
              <TableRow
                key={team.team_id}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <TableCell className="font-medium text-gray-900">
                  {team.abbreviation}
                </TableCell>
                <TableCell className="text-center">{team.wins}</TableCell>
                <TableCell className="text-center">{team.losses}</TableCell>
                <TableCell className="text-center">
                  {(team.win_pct * 100).toFixed(1)}%
                </TableCell>
                <TableCell className="text-center">
                  {team.games_back.toFixed(1)}
                </TableCell>
              </TableRow>
            ))}
            {teams.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="px-4 py-6 text-center text-gray-500"
                >
                  No standings available.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

interface PageProps {
  searchParams: Promise<{ year?: string; view?: StandingsView }>;
}

export default async function StandingsPage({ searchParams }: PageProps) {
  const seasons = await getSeasons();
  const params = await searchParams;
  const current = seasons.find((season) => season.is_active) || seasons[0];

  if (!current) {
    return (
      <div className="mx-auto max-w-4xl py-12 text-center text-gray-500">
        Standings unavailable.
      </div>
    );
  }

  const seasonYear = params.year
    ? Number(params.year) || current.year
    : current.year;
  const view = params.view === "league" ? "league" : "conference";
  const standings = await getStandings(seasonYear, view);

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-12">
      <header className="text-center">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          Standings
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          {seasonYear} season snapshot
        </p>
      </header>

      <form
        method="GET"
        className="flex flex-col items-center justify-center gap-4 md:flex-row"
      >
        <select
          name="year"
          defaultValue={seasonYear}
          className="rounded-full border border-slate-300 px-4 py-2 text-sm uppercase tracking-[0.2em]"
        >
          {seasons.map((season) => (
            <option key={season.season_id} value={season.year}>
              {season.year}
            </option>
          ))}
        </select>
        <select
          name="view"
          defaultValue={view}
          className="rounded-full border border-slate-300 px-4 py-2 text-sm uppercase tracking-[0.2em]"
        >
          <option value="conference">Conference</option>
          <option value="league">League</option>
        </select>
        <button
          type="submit"
          className="rounded-full bg-slate-900 px-6 py-2 text-xs uppercase tracking-[0.3em] text-white"
        >
          Update
        </button>
      </form>

      {view === "league" ? (
        <StandingsTable
          title="League Standings"
          teams={standings.league || []}
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <StandingsTable
            title="Eastern Conference"
            teams={standings.eastern || []}
          />
          <StandingsTable
            title="Western Conference"
            teams={standings.western || []}
          />
        </div>
      )}
    </div>
  );
}

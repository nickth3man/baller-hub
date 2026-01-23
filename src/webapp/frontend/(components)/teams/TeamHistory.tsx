import { TeamHistorySeason } from "@/types";

export function TeamHistory({ seasons }: { seasons: TeamHistorySeason[] }) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Franchise History</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Season</th>
              <th className="px-3 py-3 text-center">W</th>
              <th className="px-3 py-3 text-center">L</th>
              <th className="px-3 py-3 text-center">Win%</th>
              <th className="px-3 py-3 text-center">Playoffs</th>
            </tr>
          </thead>
          <tbody>
            {seasons.map((season, idx) => (
              <tr
                key={season.year}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <td className="px-4 py-3 font-medium">{season.year}</td>
                <td className="px-3 py-3 text-center">{season.wins}</td>
                <td className="px-3 py-3 text-center">{season.losses}</td>
                <td className="px-3 py-3 text-center">
                  {(season.win_pct * 100).toFixed(1)}%
                </td>
                <td className="px-3 py-3 text-center text-xs uppercase tracking-[0.2em]">
                  {season.made_playoffs ? season.playoff_round || "Yes" : "No"}
                </td>
              </tr>
            ))}
            {seasons.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No historical records available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import { TeamSeasonStats } from "@/types";

export function TeamStats({ stats }: { stats: TeamSeasonStats | null }) {
  if (!stats) {
    return (
      <div className="mb-6 rounded-lg bg-white p-6 shadow-md">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Season Stats
        </h2>
        <p className="text-sm text-gray-500">
          Stats unavailable for this season.
        </p>
      </div>
    );
  }

  return (
    <div className="mb-6 rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Season Stats</h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">{stats.wins}</p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Wins
          </p>
        </div>
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">{stats.losses}</p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Losses
          </p>
        </div>
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">
            {stats.points_per_game?.toFixed(1) ?? "-"}
          </p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            PPG
          </p>
        </div>
        <div className="rounded-xl bg-orange-50 p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">
            {stats.points_allowed_per_game?.toFixed(1) ?? "-"}
          </p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Opp PPG
          </p>
        </div>
      </div>
    </div>
  );
}

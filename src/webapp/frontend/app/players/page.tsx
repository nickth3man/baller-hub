import { Metadata } from "next";
import Link from "next/link";
import { getPlayers } from "@/lib/api";

export const metadata: Metadata = {
  title: "Players | Basketball Reference",
  description: "Browse all NBA players, past and present.",
};

interface PageProps {
  searchParams: Promise<{
    page?: string;
    search?: string;
    position?: string;
    is_active?: string;
  }>;
}

export default async function PlayersPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const page = Number(params.page) || 1;
  const perPage = 25;
  const search = params.search || "";
  const position = params.position || "";
  const isActiveParam = params.is_active;
  const isActive =
    isActiveParam === "true"
      ? true
      : isActiveParam === "false"
        ? false
        : undefined;

  const data = await getPlayers({
    page,
    per_page: perPage,
    search,
    position,
    is_active: isActive,
  });

  return (
    <div className="animate-in fade-in space-y-8 duration-500">
      <div className="border-b border-gray-200 pb-5">
        <h1 className="font-display text-4xl uppercase tracking-[0.2em] text-gray-900">
          Player Directory
        </h1>
        <p className="mt-2 text-lg text-gray-500">
          Browse through the history of the league, from legends to rising
          stars.
        </p>
      </div>

      {/* Advanced Filters */}
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <form
          method="GET"
          action="/players"
          className="grid grid-cols-1 items-end gap-6 md:grid-cols-4"
        >
          <div className="space-y-1">
            <label
              htmlFor="search"
              className="block text-xs font-bold uppercase tracking-widest text-gray-400"
            >
              Search Player
            </label>
            <div className="relative">
              <input
                type="text"
                id="search"
                name="search"
                defaultValue={search}
                placeholder="e.g. Stephen Curry"
                className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm outline-none transition-all focus:border-transparent focus:ring-2 focus:ring-blue-900"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label
              htmlFor="position"
              className="block text-xs font-bold uppercase tracking-widest text-gray-400"
            >
              Position
            </label>
            <select
              id="position"
              name="position"
              defaultValue={position}
              className="w-full appearance-none rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm outline-none transition-all focus:border-transparent focus:ring-2 focus:ring-blue-900"
            >
              <option value="">All Positions</option>
              <option value="G">Guard</option>
              <option value="F">Forward</option>
              <option value="C">Center</option>
              <option value="G-F">Guard-Forward</option>
              <option value="F-C">Forward-Center</option>
            </select>
          </div>

          <div className="space-y-1">
            <label
              htmlFor="is_active"
              className="block text-xs font-bold uppercase tracking-widest text-gray-400"
            >
              Status
            </label>
            <select
              id="is_active"
              name="is_active"
              defaultValue={isActiveParam || ""}
              className="w-full appearance-none rounded-lg border border-gray-300 bg-gray-50 px-4 py-2.5 text-sm outline-none transition-all focus:border-transparent focus:ring-2 focus:ring-blue-900"
            >
              <option value="">All Statuses</option>
              <option value="true">Active Players</option>
              <option value="false">Retired / Inactive</option>
            </select>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              className="flex-1 rounded-lg bg-blue-900 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-900/20 transition-all hover:bg-blue-800 active:scale-95"
            >
              Apply Filters
            </button>
            <Link
              href="/players"
              className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-600 transition-all hover:bg-gray-50"
            >
              Reset
            </Link>
          </div>
        </form>
      </section>

      {/* Players List Table */}
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">
        <div className="flex flex-col items-center justify-between gap-4 bg-blue-900 px-8 py-5 text-white sm:flex-row">
          <div>
            <h2 className="text-xl font-bold">Roster</h2>
            <p className="mt-0.5 text-xs font-medium uppercase tracking-widest text-blue-200">
              National Basketball Association
            </p>
          </div>
          <div className="rounded-full bg-blue-800 px-4 py-1.5 text-xs font-bold tracking-tight">
            Showing {data.items.length} of {data.total.toLocaleString()} players
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-8 py-4 text-left text-[10px] font-bold uppercase tracking-tighter text-gray-400">
                  Player
                </th>
                <th className="px-8 py-4 text-left text-[10px] font-bold uppercase tracking-tighter text-gray-400">
                  Pos
                </th>
                <th className="px-8 py-4 text-left text-[10px] font-bold uppercase tracking-tighter text-gray-400">
                  Current Team
                </th>
                <th className="px-8 py-4 text-left text-[10px] font-bold uppercase tracking-tighter text-gray-400">
                  Status
                </th>
                <th className="px-8 py-4 text-left text-[10px] font-bold uppercase tracking-tighter text-gray-400">
                  Experience
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.items.map((player) => (
                <tr
                  key={player.player_id}
                  className="group transition-colors hover:bg-blue-50/30"
                >
                  <td className="whitespace-nowrap px-8 py-5">
                    <Link
                      href={`/players/${player.slug}`}
                      className="text-base font-black text-blue-900 transition-colors group-hover:text-blue-700"
                    >
                      {player.full_name}
                    </Link>
                  </td>
                  <td className="whitespace-nowrap px-8 py-5 font-medium text-gray-600">
                    {player.position?.replace("_", " ") || "-"}
                  </td>
                  <td className="whitespace-nowrap px-8 py-5 font-semibold italic text-gray-500">
                    {player.current_team || "-"}
                  </td>
                  <td className="whitespace-nowrap px-8 py-5">
                    <span
                      className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-[10px] font-black uppercase tracking-widest ${
                        player.is_active
                          ? "bg-green-100 text-green-700 ring-1 ring-inset ring-green-600/20"
                          : "bg-gray-100 text-gray-500 ring-1 ring-inset ring-gray-600/20"
                      }`}
                    >
                      {player.is_active ? "Active" : "Retired"}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-8 py-5 font-mono text-xs text-gray-400">
                    {player.debut_year || "?"}-
                    {player.final_year || (player.is_active ? "Present" : "?")}
                  </td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-8 py-20 text-center">
                    <div className="flex flex-col items-center">
                      <div className="mb-4 text-gray-200">
                        <svg
                          className="h-16 w-16"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                          />
                        </svg>
                      </div>
                      <p className="text-lg font-medium text-gray-500">
                        No players match your search.
                      </p>
                      <Link
                        href="/players"
                        className="mt-2 font-bold text-blue-900 hover:underline"
                      >
                        Clear all filters
                      </Link>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination bar */}
        {data.pages > 1 && (
          <div className="flex flex-col items-center justify-between gap-4 border-t border-gray-200 bg-gray-50 px-8 py-6 sm:flex-row">
            <div className="text-sm font-medium text-gray-500">
              Page <span className="font-black text-gray-900">{data.page}</span>{" "}
              of <span className="font-black text-gray-900">{data.pages}</span>
            </div>
            <div className="flex gap-2">
              <Link
                href={{
                  pathname: "/players",
                  query: { ...params, page: page - 1 },
                }}
                className={`rounded-lg border px-5 py-2 text-sm font-bold transition-all ${
                  page <= 1
                    ? "cursor-not-allowed border-gray-200 bg-gray-100 text-gray-300"
                    : "border-gray-300 bg-white text-gray-700 shadow-sm hover:border-blue-900 hover:text-blue-900"
                }`}
                aria-disabled={page <= 1}
                tabIndex={page <= 1 ? -1 : undefined}
                style={page <= 1 ? { pointerEvents: "none" } : {}}
              >
                Previous
              </Link>
              <Link
                href={{
                  pathname: "/players",
                  query: { ...params, page: page + 1 },
                }}
                className={`rounded-lg border px-5 py-2 text-sm font-bold transition-all ${
                  page >= data.pages
                    ? "cursor-not-allowed border-gray-200 bg-gray-100 text-gray-300"
                    : "border-gray-300 bg-white text-gray-700 shadow-sm hover:border-blue-900 hover:text-blue-900"
                }`}
                aria-disabled={page >= data.pages}
                tabIndex={page >= data.pages ? -1 : undefined}
                style={page >= data.pages ? { pointerEvents: "none" } : {}}
              >
                Next
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

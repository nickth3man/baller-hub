import Link from "next/link";
import { getDrafts } from "@/lib/api";

export default async function DraftsPage() {
  const drafts = await getDrafts();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-12">
      <header className="text-center">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          NBA Drafts
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          Historical draft classes and picks.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {drafts.map((draft) => (
          <Link
            key={draft.draft_id}
            href={`/draft/${draft.year}`}
            className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:border-blue-900/30 hover:shadow-xl"
          >
            <div className="relative z-10">
              <h3 className="text-2xl font-black text-gray-900 group-hover:text-blue-900">
                {draft.year} Draft
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {draft.round_count} Rounds • {draft.pick_count} Picks
              </p>
            </div>
          </Link>
        ))}
        {drafts.length === 0 && (
          <div className="col-span-full py-20 text-center text-gray-500">
            No draft data available.
          </div>
        )}
      </div>
    </div>
  );
}

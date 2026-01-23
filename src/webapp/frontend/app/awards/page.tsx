import Link from "next/link";
import { getAwards } from "@/lib/api";

export default async function AwardsPage() {
  const awards = await getAwards();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-12">
      <header className="text-center">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          NBA Awards
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          Individual honors and team accomplishments.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {awards.map((award) => (
          <Link
            key={award.award_id}
            href={`/awards/${award.award_id}`}
            className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:border-blue-900/30 hover:shadow-xl"
          >
            <div className="relative z-10">
              <h3 className="text-2xl font-black text-gray-900 group-hover:text-blue-900">
                {award.name}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {award.category.replace(/_/g, " ")}
              </p>
              {award.description && (
                <p className="mt-4 line-clamp-2 text-sm text-gray-400">
                  {award.description}
                </p>
              )}
            </div>
          </Link>
        ))}
        {awards.length === 0 && (
          <div className="col-span-full py-20 text-center text-gray-500">
            No award data available.
          </div>
        )}
      </div>
    </div>
  );
}

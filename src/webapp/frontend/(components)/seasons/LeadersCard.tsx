import Link from "next/link";
import { SeasonLeaders } from "@/types";

export function LeadersCard({
  title,
  unit,
  leaders,
}: {
  title: string;
  unit: string;
  leaders: SeasonLeaders;
}) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-lg">
      <h3 className="mb-3 font-semibold text-gray-900">{title}</h3>
      <ol className="space-y-2">
        {leaders.leaders.map((leader) => (
          <li
            key={leader.player_slug}
            className="flex items-center justify-between text-sm"
          >
            <Link
              href={`/players/${leader.player_slug}`}
              className="truncate font-medium text-blue-600 hover:text-blue-800"
            >
              {leader.player_name}
            </Link>
            <span className="text-gray-500">
              {leader.value.toFixed(1)} {unit}
            </span>
          </li>
        ))}
        {leaders.leaders.length === 0 && (
          <li className="text-xs text-gray-400">No leader data.</li>
        )}
      </ol>
    </div>
  );
}

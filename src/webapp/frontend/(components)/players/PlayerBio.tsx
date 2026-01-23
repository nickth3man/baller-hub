import { Player } from "@/types";

function formatHeight(inches: number | null): string {
  if (!inches) return "-";
  const feet = Math.floor(inches / 12);
  const remainingInches = Math.round(inches % 12);
  return `${feet}'${remainingInches}"`;
}

export function PlayerBio({ player }: { player: Player }) {
  return (
    <div className="mb-6 rounded-2xl bg-white p-6 shadow-lg">
      <div className="flex items-start gap-6">
        {/* Photo placeholder */}
        <div className="flex h-40 w-32 items-center justify-center rounded-lg bg-gray-200 text-gray-400">
          <svg className="h-16 w-16" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
        </div>

        <div className="flex-1">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">
            {player.full_name}
          </h1>

          <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
            <div>
              <span className="text-gray-500">Position</span>
              <p className="font-medium">
                {player.position?.replace("_", " ") || "-"}
              </p>
            </div>
            <div>
              <span className="text-gray-500">Height</span>
              <p className="font-medium">
                {formatHeight(player.height_inches)}
              </p>
            </div>
            <div>
              <span className="text-gray-500">Weight</span>
              <p className="font-medium">
                {player.weight_lbs ? `${player.weight_lbs} lbs` : "-"}
              </p>
            </div>
            <div>
              <span className="text-gray-500">Born</span>
              <p className="font-medium">
                {player.birth_date || "-"}
                {player.birth_place_city && ` in ${player.birth_place_city}`}
              </p>
            </div>
            <div>
              <span className="text-gray-500">College</span>
              <p className="font-medium">{player.college || "-"}</p>
            </div>
            <div>
              <span className="text-gray-500">High School</span>
              <p className="font-medium">{player.high_school || "-"}</p>
            </div>
            <div>
              <span className="text-gray-500">Draft</span>
              <p className="font-medium">
                {player.draft_year
                  ? `${player.draft_year} (Pick ${player.draft_pick})`
                  : "Undrafted"}
              </p>
            </div>
            <div>
              <span className="text-gray-500">Experience</span>
              <p className="font-medium">
                {player.debut_year && player.final_year
                  ? `${player.debut_year}-${player.is_active ? "Present" : player.final_year}`
                  : "-"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

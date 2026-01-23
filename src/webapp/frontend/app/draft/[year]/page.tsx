import { notFound } from "next/navigation";
import { getDraft } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/(components)/ui/Table";
import Link from "next/link";

interface PageProps {
  params: Promise<{ year: string }>;
}

export default async function DraftDetailPage({ params }: PageProps) {
  const { year } = await params;
  const draftYear = parseInt(year, 10);

  if (isNaN(draftYear)) {
    notFound();
  }

  let draft;
  try {
    draft = await getDraft(draftYear);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-12">
      <header className="text-center">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          {draftYear} NBA Draft
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          {draft.draft_date || "Date TBD"} • {draft.pick_count} Total Picks
        </p>
      </header>

      <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead className="w-[10%] text-center">Pick</TableHead>
              <TableHead className="w-[10%] text-center">Round</TableHead>
              <TableHead className="w-[30%]">Player</TableHead>
              <TableHead className="w-[20%]">Team</TableHead>
              <TableHead className="w-[30%]">College</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {draft.picks?.map((pick, idx) => (
              <TableRow
                key={pick.pick_id}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <TableCell className="text-center font-bold">
                  {pick.overall_pick}
                </TableCell>
                <TableCell className="text-center text-gray-500">
                  {pick.round_number}
                </TableCell>
                <TableCell>
                  {pick.player_id ? (
                    <Link
                      href={`/players/${pick.player_id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {pick.player_name || pick.player_id}
                    </Link>
                  ) : (
                    pick.player_name || "Unknown"
                  )}
                </TableCell>
                <TableCell className="font-medium">
                  {pick.team_abbrev || pick.team_id}
                </TableCell>
                <TableCell className="text-gray-500">
                  {pick.college || "-"}
                </TableCell>
              </TableRow>
            ))}
            {(!draft.picks || draft.picks.length === 0) && (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="py-10 text-center text-gray-500"
                >
                  No pick data available for this draft.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

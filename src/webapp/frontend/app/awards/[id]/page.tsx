import { notFound } from "next/navigation";
import { getAward } from "@/lib/api";
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
  params: Promise<{ id: string }>;
}

export default async function AwardDetailPage({ params }: PageProps) {
  const { id } = await params;
  const awardId = parseInt(id, 10);

  if (isNaN(awardId)) {
    notFound();
  }

  let award;
  try {
    award = await getAward(awardId);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-12">
      <header className="text-center">
        <h1 className="font-display text-5xl uppercase tracking-[0.2em] text-gray-900">
          {award.name}
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          {award.description || "Award history and recipients."}
        </p>
      </header>

      <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead className="w-[15%] text-center">Season</TableHead>
              <TableHead className="w-[40%]">Winner</TableHead>
              <TableHead className="w-[15%]">Team</TableHead>
              <TableHead className="w-[15%] text-center">Rank</TableHead>
              <TableHead className="w-[15%]">Notes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {award.recipients?.map((recipient, idx) => (
              <TableRow
                key={`${recipient.season_id}-${recipient.player_id}-${recipient.team_id}`}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <TableCell className="text-center font-bold">
                  {recipient.season_year}
                </TableCell>
                <TableCell>
                  {recipient.player_id ? (
                    <Link
                      href={`/players/${recipient.player_id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {recipient.player_name || recipient.player_id}
                    </Link>
                  ) : (
                    recipient.player_name || "Multiple/Team"
                  )}
                </TableCell>
                <TableCell className="font-medium">
                  {recipient.team_abbrev || recipient.team_id || "-"}
                </TableCell>
                <TableCell className="text-center">
                  {recipient.vote_rank || 1}
                </TableCell>
                <TableCell className="text-sm text-gray-500">
                  {recipient.notes || "-"}
                </TableCell>
              </TableRow>
            ))}
            {(!award.recipients || award.recipients.length === 0) && (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="py-10 text-center text-gray-500"
                >
                  No recipient data available for this award.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

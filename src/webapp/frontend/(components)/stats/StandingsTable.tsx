import { StandingsTeam } from "@/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/(components)/ui/Table";

interface StandingsTableProps {
  title: string;
  teams: StandingsTeam[];
}

export function StandingsTable({ title, teams }: StandingsTableProps) {
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

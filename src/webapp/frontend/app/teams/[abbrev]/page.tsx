import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getTeam,
  getTeamHistory,
  getTeamRoster,
  getTeamSchedule,
  getTeamStats,
} from "@/lib/api";
import { Team } from "@/types";
import { TeamHeader } from "@/(components)/teams/TeamHeader";
import { RosterTable } from "@/(components)/teams/RosterTable";
import { TeamStats } from "@/(components)/teams/TeamStats";
import { RecentGames } from "@/(components)/teams/RecentGames";
import { TeamHistory } from "@/(components)/teams/TeamHistory";

interface PageProps {
  params: Promise<{ abbrev: string }>;
}

const now = new Date();
const currentSeasonYear =
  now.getMonth() >= 9 ? now.getFullYear() + 1 : now.getFullYear();

export default async function TeamPage({ params }: PageProps) {
  const { abbrev } = await params;

  let team: Team;
  try {
    team = await getTeam(abbrev);
  } catch {
    notFound();
  }

  const [rosterResult, statsResult, scheduleResult] = await Promise.allSettled([
    getTeamRoster(abbrev, currentSeasonYear),
    getTeamStats(abbrev, currentSeasonYear),
    getTeamSchedule(abbrev, currentSeasonYear),
  ]);
  const historyResult = await getTeamHistory(abbrev).catch(() => []);

  const roster = rosterResult.status === "fulfilled" ? rosterResult.value : [];
  const stats = statsResult.status === "fulfilled" ? statsResult.value : null;
  const schedule =
    scheduleResult.status === "fulfilled" ? scheduleResult.value : [];

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link href="/teams" className="hover:text-blue-600">
            Teams
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">
            {team.city} {team.name}
          </span>
        </nav>

        <TeamHeader team={team} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <RosterTable roster={roster} seasonYear={currentSeasonYear} />
            <TeamHistory seasons={historyResult.slice(0, 10)} />
          </div>

          <div>
            <TeamStats stats={stats} />
            <RecentGames games={schedule} />
          </div>
        </div>
      </div>
    </div>
  );
}

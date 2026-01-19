"use client";

import Link from "next/link";

export function LeagueLeaders() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <LeaderCategory
        title="Points"
        leaders={[
          { name: "Giannis Antetokounmpo", slug: "antetgi01", value: "31.2" },
          { name: "Shai Gilgeous-Alexander", slug: "gilMDsha01", value: "30.8" },
          { name: "Luka Doncic", slug: "doncilu01", value: "28.5" },
        ]}
        unit="PPG"
      />
      <LeaderCategory
        title="Rebounds"
        leaders={[
          { name: "Domantas Sabonis", slug: "sabondo01", value: "14.2" },
          { name: "Rudy Gobert", slug: "goberru01", value: "11.8" },
          { name: "Victor Wembanyama", slug: "wembavi01", value: "11.5" },
        ]}
        unit="RPG"
      />
      <LeaderCategory
        title="Assists"
        leaders={[
          { name: "Trae Young", slug: "youngtr01", value: "11.8" },
          { name: "Tyrese Haliburton", slug: "halibty01", value: "10.5" },
          { name: "Luka Doncic", slug: "doncilu01", value: "9.2" },
        ]}
        unit="APG"
      />
      <LeaderCategory
        title="Steals"
        leaders={[
          { name: "De'Aaron Fox", slug: "foxde01", value: "2.1" },
          { name: "Victor Wembanyama", slug: "wembavi01", value: "1.9" },
          { name: "Shai Gilgeous-Alexander", slug: "gilgesh01", value: "1.8" },
        ]}
        unit="SPG"
      />
      <LeaderCategory
        title="Blocks"
        leaders={[
          { name: "Victor Wembanyama", slug: "wembavi01", value: "3.8" },
          { name: "Chet Holmgren", slug: "holmgch01", value: "2.5" },
          { name: "Rudy Gobert", slug: "goberru01", value: "2.3" },
        ]}
        unit="BPG"
      />
    </div>
  );
}

interface Leader {
  name: string;
  slug: string;
  value: string;
}

interface LeaderCategoryProps {
  title: string;
  leaders: Leader[];
  unit: string;
}

function LeaderCategory({ title, leaders, unit }: LeaderCategoryProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold text-gray-900 mb-3">{title}</h3>
      <ol className="space-y-2">
        {leaders.map((leader, i) => (
          <li key={leader.slug} className="flex items-start">
            <span className="text-gray-400 text-sm mr-2">{i + 1}.</span>
            <div className="flex-1 min-w-0">
              <Link
                href={`/players/${leader.slug}`}
                className="text-sm font-medium text-gray-900 hover:text-primary-600 truncate block"
              >
                {leader.name}
              </Link>
              <span className="text-sm text-primary-600 font-semibold">
                {leader.value} {unit}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

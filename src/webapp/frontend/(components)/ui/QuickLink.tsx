import Link from "next/link";

interface QuickLinkProps {
  href: string;
  title: string;
  description: string;
}

export function QuickLink({ href, title, description }: QuickLinkProps) {
  return (
    <Link
      href={href}
      className="group block rounded-2xl border border-gray-200 bg-white p-4 shadow transition-shadow hover:shadow-xl"
    >
      <h3 className="font-semibold text-gray-900 transition-colors group-hover:text-orange-600">
        {title}
      </h3>
      <p className="text-sm text-gray-500">{description}</p>
    </Link>
  );
}

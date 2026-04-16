import Link from "next/link";
import type { KnowledgePointBrief, UserProgress } from "@/lib/types";

interface KnowledgeCardProps {
  point: KnowledgePointBrief;
  progress?: UserProgress;
}

const HEAT_DISPLAY = ["", "🔥", "🔥🔥", "🔥🔥🔥"];
const UTILITY_DISPLAY = ["", "⭐", "⭐⭐", "⭐⭐⭐"];

const MASTERY_STYLES: Record<string, { border: string; badge: string; label: string }> = {
  mastered: {
    border: "border-green-300",
    badge: "bg-green-100 text-green-700",
    label: "已掌握",
  },
  partial: {
    border: "border-amber-300",
    badge: "bg-amber-100 text-amber-700",
    label: "部分掌握",
  },
  not_started: {
    border: "border-gray-200",
    badge: "bg-gray-100 text-gray-500",
    label: "未学习",
  },
};

export default function KnowledgeCard({ point, progress }: KnowledgeCardProps) {
  const mastery = progress?.mastery || "not_started";
  const styles = MASTERY_STYLES[mastery];

  return (
    <Link href={`/learn/${point.id}`}>
      <div
        className={`relative rounded-xl border p-4 transition-shadow hover:shadow-md ${styles.border} ${
          mastery === "not_started" && !progress ? "opacity-70" : ""
        }`}
      >
        <span
          className={`absolute right-2 top-2 rounded-full px-2 py-0.5 text-xs ${styles.badge}`}
        >
          {styles.label}
        </span>
        <div className="mb-2 flex gap-2 text-xs">
          <span className="text-red-500">{HEAT_DISPLAY[point.interview_heat]}</span>
          <span className="text-gray-400">{UTILITY_DISPLAY[point.dev_utility]}</span>
        </div>
        <h4 className="mb-1 text-sm font-semibold text-gray-900">{point.title}</h4>
        <p className="line-clamp-2 text-xs text-gray-500">{point.scenario}</p>
        <div className="mt-3 flex flex-wrap gap-1">
          {point.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </Link>
  );
}

interface SelfRatingProps {
  onRate: (score: "mastered" | "partial" | "unfamiliar") => void;
}

const RATINGS = [
  {
    value: "mastered" as const,
    label: "完全掌握",
    color: "bg-green-500 hover:bg-green-600",
    desc: "能流畅讲出使用场景和代码",
  },
  {
    value: "partial" as const,
    label: "部分掌握",
    color: "bg-amber-500 hover:bg-amber-600",
    desc: "知道概念但代码细节不确定",
  },
  {
    value: "unfamiliar" as const,
    label: "不熟悉",
    color: "bg-red-500 hover:bg-red-600",
    desc: "完全不记得或没学过",
  },
];

export default function SelfRating({ onRate }: SelfRatingProps) {
  return (
    <div className="mt-6 rounded-lg border-2 border-dashed border-gray-300 p-6">
      <h3 className="mb-4 text-center text-sm font-semibold text-gray-600">
        自评一下你的掌握程度
      </h3>
      <div className="flex gap-3">
        {RATINGS.map((r) => (
          <button
            key={r.value}
            onClick={() => onRate(r.value)}
            className={`flex-1 rounded-lg px-4 py-3 text-white ${r.color}`}
          >
            <div className="text-sm font-semibold">{r.label}</div>
            <div className="mt-1 text-xs opacity-80">{r.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

"use client";

interface FilterBarProps {
  categories: string[];
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
}

const SORT_OPTIONS = [
  { value: "sort_order", label: "学习路径" },
  { value: "interview_heat", label: "面试热度" },
  { value: "dev_utility", label: "开发实用度" },
];

export default function FilterBar({
  categories,
  selectedCategory,
  onCategoryChange,
  sortBy,
  onSortChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex gap-2">
        <button
          onClick={() => onCategoryChange(null)}
          className={`rounded-full px-3 py-1 text-sm ${
            selectedCategory === null
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          全部
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => onCategoryChange(cat)}
            className={`rounded-full px-3 py-1 text-sm ${
              selectedCategory === cat
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>
      <div className="ml-auto flex items-center gap-2 text-xs text-gray-500">
        <span>排序：</span>
        {SORT_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onSortChange(opt.value)}
            className={`${
              sortBy === opt.value
                ? "font-semibold text-blue-600"
                : "hover:text-gray-900"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}

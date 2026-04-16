"use client";

import { useEffect, useState } from "react";
import { getPoints, getProgress } from "@/lib/api";
import type { KnowledgePointBrief, UserProgress } from "@/lib/types";
import KnowledgeCard from "@/components/KnowledgeCard";
import FilterBar from "@/components/FilterBar";

const LEVEL_TABS = [
  { value: null, label: "全部" },
  { value: "basic", label: "基础" },
  { value: "intermediate", label: "进阶" },
  { value: "advanced", label: "高级" },
];

export default function LearnPage() {
  const [points, setPoints] = useState<KnowledgePointBrief[]>([]);
  const [progressMap, setProgressMap] = useState<Record<number, UserProgress>>({});
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState("sort_order");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [pts, prog] = await Promise.all([
        getPoints({
          category: selectedCategory || undefined,
          level: selectedLevel || undefined,
          sort: sortBy,
        }),
        getProgress(),
      ]);
      setPoints(pts);
      const map: Record<number, UserProgress> = {};
      for (const p of prog) {
        map[p.point_id] = p;
      }
      setProgressMap(map);
      setLoading(false);
    }
    load();
  }, [selectedCategory, selectedLevel, sortBy]);

  const categories = [...new Set(points.map((p) => p.category))];

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold">学习路径</h1>
      <p className="mb-6 text-sm text-gray-500">
        按场景学习 LangChain 和 LangGraph 的核心知识点
      </p>

      {/* Level tabs */}
      <div className="mb-4 flex gap-2">
        {LEVEL_TABS.map((tab) => (
          <button
            key={tab.label}
            onClick={() => setSelectedLevel(tab.value)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              selectedLevel === tab.value
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 hover:bg-gray-100"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <FilterBar
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        sortBy={sortBy}
        onSortChange={setSortBy}
      />

      {loading ? (
        <div className="mt-12 text-center text-gray-400">加载中...</div>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {points.map((point) => (
            <KnowledgeCard
              key={point.id}
              point={point}
              progress={progressMap[point.id]}
            />
          ))}
        </div>
      )}
    </div>
  );
}

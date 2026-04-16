"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { startInterview } from "@/lib/api";

const CATEGORIES = [
  { value: "Prompt", label: "Prompt" },
  { value: "Output", label: "Output" },
  { value: "Chain", label: "Chain" },
  { value: "Model", label: "Model" },
  { value: "Memory", label: "Memory" },
  { value: "Retrieval", label: "Retrieval" },
  { value: "Tools", label: "Tools" },
  { value: "Agent", label: "Agent" },
  { value: "Graph", label: "Graph" },
];

const LEVELS = [
  { value: "basic", label: "基础" },
  { value: "intermediate", label: "进阶" },
  { value: "advanced", label: "高级" },
];

const STRATEGIES = [
  { value: "smart", label: "智能优先", desc: "优先出你不熟的题" },
  { value: "random", label: "随机", desc: "完全随机抽取" },
  { value: "sequential", label: "顺序", desc: "按学习路径顺序" },
];

const COUNT_OPTIONS = [5, 10, 15, 20];

export default function InterviewSetupPage() {
  const router = useRouter();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [heatFilter, setHeatFilter] = useState(1);
  const [count, setCount] = useState(10);
  const [strategy, setStrategy] = useState("smart");
  const [starting, setStarting] = useState(false);

  const toggleCategory = (cat: string) => {
    setSelectedCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  const toggleLevel = (level: string) => {
    setSelectedLevels((prev) =>
      prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]
    );
  };

  const handleStart = async () => {
    setStarting(true);
    const result = await startInterview({
      categories: selectedCategories.length > 0 ? selectedCategories : undefined,
      levels: selectedLevels.length > 0 ? selectedLevels : undefined,
      min_heat: heatFilter,
      count,
      strategy: strategy as "smart" | "random" | "sequential",
    });
    // Store session data in sessionStorage for the session page
    sessionStorage.setItem("interview_session", JSON.stringify(result));
    router.push("/interview/session");
  };

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-2 text-2xl font-bold">模拟面试</h1>
      <p className="mb-8 text-sm text-gray-500">配置面试参数，开始模拟</p>

      {/* Categories */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          题目范围
        </h3>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => toggleCategory(cat.value)}
              className={`rounded-full px-3 py-1 text-sm ${
                selectedCategories.includes(cat.value)
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {cat.label}
            </button>
          ))}
          {selectedCategories.length > 0 && (
            <button
              onClick={() => setSelectedCategories([])}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              清除
            </button>
          )}
        </div>
        {selectedCategories.length === 0 && (
          <p className="mt-1 text-xs text-gray-400">未选择 = 全部分类</p>
        )}
      </div>

      {/* Levels */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          难度
        </h3>
        <div className="flex gap-2">
          {LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => toggleLevel(level.value)}
              className={`rounded-lg px-4 py-2 text-sm ${
                selectedLevels.includes(level.value)
                  ? "bg-purple-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {level.label}
            </button>
          ))}
        </div>
        {selectedLevels.length === 0 && (
          <p className="mt-1 text-xs text-gray-400">未选择 = 全部难度</p>
        )}
      </div>

      {/* Heat filter */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          面试热度筛选
        </h3>
        <div className="flex gap-2">
          {[1, 2, 3].map((h) => (
            <button
              key={h}
              onClick={() => setHeatFilter(h)}
              className={`rounded-lg px-4 py-2 text-sm ${
                heatFilter === h
                  ? "bg-red-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {h === 1 ? "全部" : h === 2 ? "🔥🔥 中频以上" : "🔥🔥🔥 仅高频"}
            </button>
          ))}
        </div>
      </div>

      {/* Count */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          题数
        </h3>
        <div className="flex gap-2">
          {COUNT_OPTIONS.map((n) => (
            <button
              key={n}
              onClick={() => setCount(n)}
              className={`rounded-lg px-4 py-2 text-sm ${
                count === n
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {n} 题
            </button>
          ))}
        </div>
      </div>

      {/* Strategy */}
      <div className="mb-8">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          出题策略
        </h3>
        <div className="flex gap-3">
          {STRATEGIES.map((s) => (
            <button
              key={s.value}
              onClick={() => setStrategy(s.value)}
              className={`flex-1 rounded-lg border-2 p-3 text-center ${
                strategy === s.value
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="text-sm font-semibold">{s.label}</div>
              <div className="text-xs text-gray-500">{s.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Start button */}
      <button
        onClick={handleStart}
        disabled={starting}
        className="w-full rounded-lg bg-purple-600 py-3 text-lg font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
      >
        {starting ? "正在生成题目..." : "开始面试"}
      </button>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getPoint, getProgress, updateMastery, toggleFavorite } from "@/lib/api";
import type { KnowledgePoint, UserProgress } from "@/lib/types";
import CodeBlock from "@/components/CodeBlock";
import Link from "next/link";

const HEAT_DISPLAY = ["", "🔥", "🔥🔥", "🔥🔥🔥"];
const UTILITY_DISPLAY = ["", "⭐", "⭐⭐", "⭐⭐⭐"];
const LEVEL_LABELS: Record<string, string> = {
  basic: "基础",
  intermediate: "进阶",
  advanced: "高级",
};

const MASTERY_OPTIONS = [
  { value: "not_started", label: "未学习", color: "bg-gray-100 text-gray-600" },
  { value: "partial", label: "部分掌握", color: "bg-amber-100 text-amber-700" },
  { value: "mastered", label: "已掌握", color: "bg-green-100 text-green-700" },
];

export default function PointDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [point, setPoint] = useState<KnowledgePoint | null>(null);
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [pt, allProgress] = await Promise.all([getPoint(id), getProgress()]);
      setPoint(pt);
      setProgress(allProgress.find((p) => p.point_id === id) || null);
      setLoading(false);
    }
    load();
  }, [id]);

  const handleMastery = async (mastery: string) => {
    const updated = await updateMastery(id, mastery);
    setProgress(updated);
  };

  const handleFavorite = async () => {
    const updated = await toggleFavorite(id, !progress?.is_favorite);
    setProgress(updated);
  };

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!point) {
    return <div className="mt-12 text-center text-gray-400">知识点不存在</div>;
  }

  const currentMastery = progress?.mastery || "not_started";

  return (
    <div className="mx-auto max-w-3xl">
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="mb-4 text-sm text-gray-500 hover:text-gray-900"
      >
        ← 返回
      </button>

      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <h1 className="text-2xl font-bold">{point.title}</h1>
            <span className="rounded-full bg-blue-100 px-3 py-0.5 text-xs text-blue-700">
              {LEVEL_LABELS[point.level] || point.level}
            </span>
          </div>
          <div className="flex gap-4 text-sm text-gray-500">
            <span>面试热度：{HEAT_DISPLAY[point.interview_heat]}</span>
            <span>开发实用度：{UTILITY_DISPLAY[point.dev_utility]}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleFavorite}
            className={`rounded-lg border px-3 py-1.5 text-sm ${
              progress?.is_favorite
                ? "border-amber-300 bg-amber-50 text-amber-600"
                : "border-gray-200 text-gray-500 hover:bg-gray-50"
            }`}
          >
            {progress?.is_favorite ? "★ 已收藏" : "☆ 收藏"}
          </button>
        </div>
      </div>

      {/* Scenario */}
      <div className="mb-6 rounded-r-lg border-l-4 border-blue-500 bg-blue-50 px-5 py-4">
        <div className="mb-1 font-semibold text-blue-800">💡 使用场景</div>
        <div className="text-gray-700">{point.scenario}</div>
      </div>

      {/* Code */}
      <div className="mb-6">
        <h3 className="mb-2 font-semibold text-gray-800">📝 代码示例</h3>
        <CodeBlock code={point.code_example} />
      </div>

      {/* Key Points */}
      <div className="mb-6">
        <h3 className="mb-2 font-semibold text-gray-800">🎯 核心要点</h3>
        <div className="space-y-2">
          {point.key_points.map((kp, i) => (
            <div key={i} className="flex gap-2 text-sm">
              <span className="font-bold text-green-500">✓</span>
              <span>{kp}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Common Mistakes */}
      <div className="mb-6">
        <h3 className="mb-2 font-semibold text-gray-800">⚠️ 常见误区</h3>
        <div className="rounded-lg bg-red-50 p-4">
          {point.common_mistakes.map((cm, i) => (
            <div key={i} className="flex gap-2 text-sm">
              <span className="text-red-500">✗</span>
              <span>{cm}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Related Points */}
      {point.related_point_ids.length > 0 && (
        <div className="mb-6">
          <h3 className="mb-2 font-semibold text-gray-800">🔗 关联知识点</h3>
          <div className="flex flex-wrap gap-2">
            {point.related_point_ids.map((rid) => (
              <Link
                key={rid}
                href={`/learn/${rid}`}
                className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
              >
                #{rid}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Mastery Control */}
      <div className="rounded-lg border bg-white p-4">
        <h3 className="mb-3 text-sm font-semibold text-gray-600">标记掌握程度</h3>
        <div className="flex gap-2">
          {MASTERY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleMastery(opt.value)}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                currentMastery === opt.value
                  ? opt.color + " ring-2 ring-offset-1"
                  : "bg-gray-50 text-gray-500 hover:bg-gray-100"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

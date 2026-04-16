"use client";

import { useState } from "react";
import type { KnowledgePoint } from "@/lib/types";
import CodeBlock from "./CodeBlock";
import SelfRating from "./SelfRating";

interface InterviewQuestionProps {
  point: KnowledgePoint;
  index: number;
  total: number;
  onRate: (score: "mastered" | "partial" | "unfamiliar") => void;
}

export default function InterviewQuestion({
  point,
  index,
  total,
  onRate,
}: InterviewQuestionProps) {
  const [revealed, setRevealed] = useState(false);

  const levelLabel =
    point.level === "basic"
      ? "基础"
      : point.level === "intermediate"
        ? "进阶"
        : "高级";

  return (
    <div className="mx-auto max-w-3xl">
      {/* Progress */}
      <div className="mb-6 flex items-center justify-between">
        <span className="text-sm text-gray-500">
          第 {index + 1} / {total} 题
        </span>
        <div className="mx-4 h-2 flex-1 rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-blue-500 transition-all"
            style={{ width: `${((index + 1) / total) * 100}%` }}
          />
        </div>
      </div>

      {/* Scenario (always visible) */}
      <div className="mb-6 rounded-r-lg border-l-4 border-purple-500 bg-purple-50 px-5 py-4">
        <div className="mb-1 text-xs font-semibold uppercase text-purple-600">
          面试题
        </div>
        <div className="text-lg font-medium text-gray-800">
          {point.scenario}，你会使用什么？请说明用法和关键注意事项。
        </div>
      </div>

      {/* Hint: category and level */}
      <div className="mb-4 text-center text-sm text-gray-400">
        提示：{point.category} 分类 · {levelLabel}
      </div>

      {!revealed ? (
        <div className="text-center">
          <p className="mb-4 text-sm text-gray-500">
            先在心中组织你的答案，准备好后点击查看参考答案
          </p>
          <button
            onClick={() => setRevealed(true)}
            className="rounded-lg bg-blue-600 px-8 py-3 text-white hover:bg-blue-700"
          >
            查看答案
          </button>
        </div>
      ) : (
        <div>
          <h2 className="mb-4 text-xl font-bold">{point.title}</h2>

          {/* Code */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-600">📝 参考代码</h3>
            <CodeBlock code={point.code_example} />
          </div>

          {/* Key Points */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-600">🎯 核心要点</h3>
            <div className="space-y-1">
              {point.key_points.map((kp, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="font-bold text-green-500">✓</span>
                  <span>{kp}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Common Mistakes */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-600">⚠️ 常见误区</h3>
            <div className="rounded-lg bg-red-50 p-3">
              {point.common_mistakes.map((cm, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="text-red-500">✗</span>
                  <span>{cm}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Self rating */}
          <SelfRating onRate={onRate} />
        </div>
      )}
    </div>
  );
}

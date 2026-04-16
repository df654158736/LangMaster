"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getReport } from "@/lib/api";
import type { InterviewReport } from "@/lib/types";

export default function InterviewReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const sessionId = sessionStorage.getItem("interview_session_id");
    if (!sessionId) {
      router.push("/interview/setup");
      return;
    }
    async function load() {
      const data = await getReport(Number(sessionId));
      setReport(data);
      setLoading(false);
    }
    load();
  }, [router]);

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!report) return null;

  const total = report.results.length;
  const scorePercent =
    total > 0 ? Math.round((report.total_mastered / total) * 100) : 0;

  const weakPoints = report.results.filter(
    (r) => r.self_score === "unfamiliar" || r.self_score === "partial"
  );

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-2 text-2xl font-bold">面试报告</h1>
      <p className="mb-8 text-sm text-gray-500">
        {new Date(report.created_at).toLocaleString("zh-CN")}
      </p>

      {/* Score summary */}
      <div className="mb-8 flex justify-center gap-8">
        <div className="text-center">
          <div className="text-4xl font-bold text-green-500">
            {report.total_mastered}
          </div>
          <div className="text-sm text-gray-500">完全掌握</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-amber-500">
            {report.total_partial}
          </div>
          <div className="text-sm text-gray-500">部分掌握</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-red-500">
            {report.total_unfamiliar}
          </div>
          <div className="text-sm text-gray-500">不熟悉</div>
        </div>
      </div>

      {/* Score bar */}
      <div className="mb-8 text-center">
        <div className="text-5xl font-bold text-gray-900">{scorePercent}%</div>
        <div className="text-sm text-gray-500">掌握率</div>
      </div>

      {/* Weak points */}
      {weakPoints.length > 0 && (
        <div className="mb-8 rounded-lg bg-amber-50 p-4">
          <h3 className="mb-2 font-semibold text-amber-800">
            建议重点复习
          </h3>
          <div className="space-y-2">
            {weakPoints.map((wp) => (
              <Link
                key={wp.point_id}
                href={`/learn/${wp.point_id}`}
                className="flex items-center justify-between rounded-lg bg-white px-3 py-2 text-sm hover:bg-gray-50"
              >
                <span>知识点 #{wp.point_id}</span>
                <span
                  className={
                    wp.self_score === "unfamiliar"
                      ? "text-red-500"
                      : "text-amber-500"
                  }
                >
                  {wp.self_score === "unfamiliar" ? "不熟悉" : "部分掌握"}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <Link
          href="/interview/setup"
          className="flex-1 rounded-lg bg-purple-600 py-3 text-center text-white hover:bg-purple-700"
        >
          再来一次
        </Link>
        <Link
          href="/learn"
          className="flex-1 rounded-lg bg-gray-200 py-3 text-center text-gray-700 hover:bg-gray-300"
        >
          去学习
        </Link>
      </div>
    </div>
  );
}

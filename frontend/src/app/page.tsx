"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getDashboardStats, getWeakPoints } from "@/lib/api";
import type { DashboardStats, WeakPoint } from "@/lib/types";
import StatsCard from "@/components/StatsCard";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [weakPoints, setWeakPoints] = useState<WeakPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [s, wp] = await Promise.all([getDashboardStats(), getWeakPoints()]);
      setStats(s);
      setWeakPoints(wp);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!stats) return null;

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold">LangMaster</h1>
      <p className="mb-8 text-sm text-gray-500">
        场景驱动学习 LangChain & LangGraph
      </p>

      {/* Stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatsCard
          value={`${stats.mastered_count}/${stats.total_points}`}
          label="已掌握知识点"
          color="blue"
        />
        <StatsCard
          value={stats.interview_count}
          label="模拟面试次数"
          color="green"
        />
        <StatsCard
          value={stats.weak_count}
          label="待复习（薄弱）"
          color="yellow"
        />
        <StatsCard
          value={
            stats.last_score_percent !== null
              ? `${stats.last_score_percent}%`
              : "-"
          }
          label="最近面试得分"
          color="pink"
        />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        {/* Weak points */}
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">
            📌 推荐复习
          </h3>
          {weakPoints.length === 0 ? (
            <p className="text-sm text-gray-400">暂无薄弱知识点</p>
          ) : (
            <div className="space-y-2">
              {weakPoints.slice(0, 5).map((wp) => (
                <Link
                  key={wp.point_id}
                  href={`/learn/${wp.point_id}`}
                  className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm hover:bg-gray-100"
                >
                  <span>{wp.title}</span>
                  <span
                    className={
                      wp.mastery === "not_started"
                        ? "text-red-500"
                        : "text-amber-500"
                    }
                  >
                    {wp.mastery === "not_started" ? "不熟悉" : "部分掌握"}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">
            🚀 快捷入口
          </h3>
          <div className="space-y-2">
            <Link
              href="/learn"
              className="block rounded-lg bg-blue-500 py-3 text-center text-sm font-semibold text-white hover:bg-blue-600"
            >
              开始学习
            </Link>
            <Link
              href="/interview/setup"
              className="block rounded-lg bg-purple-500 py-3 text-center text-sm font-semibold text-white hover:bg-purple-600"
            >
              模拟面试
            </Link>
            <Link
              href="/profile"
              className="block rounded-lg bg-gray-200 py-3 text-center text-sm font-semibold text-gray-700 hover:bg-gray-300"
            >
              个人中心
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getProgress,
  getInterviewHistory,
  getDashboardStats,
} from "@/lib/api";
import type { UserProgress, InterviewReport, DashboardStats } from "@/lib/types";

export default function ProfilePage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [progress, setProgress] = useState<UserProgress[]>([]);
  const [history, setHistory] = useState<InterviewReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [s, p, h] = await Promise.all([
        getDashboardStats(),
        getProgress(),
        getInterviewHistory(),
      ]);
      setStats(s);
      setProgress(p);
      setHistory(h);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!stats) return null;

  const favorites = progress.filter((p) => p.is_favorite);
  const mastered = progress.filter((p) => p.mastery === "mastered");
  const partial = progress.filter((p) => p.mastery === "partial");

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-6 text-2xl font-bold">个人中心</h1>

      {/* Stats summary */}
      <div className="mb-8 grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-green-50 p-4 text-center">
          <div className="text-3xl font-bold text-green-700">{mastered.length}</div>
          <div className="text-xs text-gray-500">已掌握</div>
        </div>
        <div className="rounded-lg bg-amber-50 p-4 text-center">
          <div className="text-3xl font-bold text-amber-700">{partial.length}</div>
          <div className="text-xs text-gray-500">部分掌握</div>
        </div>
        <div className="rounded-lg bg-blue-50 p-4 text-center">
          <div className="text-3xl font-bold text-blue-700">{stats.total_points}</div>
          <div className="text-xs text-gray-500">总知识点</div>
        </div>
      </div>

      {/* Favorites */}
      <div className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">⭐ 收藏的知识点</h2>
        {favorites.length === 0 ? (
          <p className="text-sm text-gray-400">暂无收藏</p>
        ) : (
          <div className="space-y-2">
            {favorites.map((f) => (
              <Link
                key={f.point_id}
                href={`/learn/${f.point_id}`}
                className="block rounded-lg border px-4 py-2 text-sm hover:bg-gray-50"
              >
                知识点 #{f.point_id}
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Interview history */}
      <div>
        <h2 className="mb-3 text-lg font-semibold">📝 面试历史</h2>
        {history.length === 0 ? (
          <p className="text-sm text-gray-400">暂无面试记录</p>
        ) : (
          <div className="space-y-2">
            {history.map((h) => {
              const total = h.results.length;
              const percent =
                total > 0 ? Math.round((h.total_mastered / total) * 100) : 0;
              return (
                <div
                  key={h.id}
                  className="flex items-center justify-between rounded-lg border px-4 py-3"
                >
                  <div>
                    <div className="text-sm font-medium">
                      {total} 题 · 掌握率 {percent}%
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(h.created_at).toLocaleString("zh-CN")}
                    </div>
                  </div>
                  <div className="flex gap-3 text-sm">
                    <span className="text-green-500">
                      ✓ {h.total_mastered}
                    </span>
                    <span className="text-amber-500">
                      ~ {h.total_partial}
                    </span>
                    <span className="text-red-500">
                      ✗ {h.total_unfamiliar}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

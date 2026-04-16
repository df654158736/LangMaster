"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { submitAnswer } from "@/lib/api";
import type { InterviewStartResult } from "@/lib/types";
import InterviewQuestion from "@/components/InterviewQuestion";

export default function InterviewSessionPage() {
  const router = useRouter();
  const [session, setSession] = useState<InterviewStartResult | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const stored = sessionStorage.getItem("interview_session");
    if (!stored) {
      router.push("/interview/setup");
      return;
    }
    setSession(JSON.parse(stored));
  }, [router]);

  if (!session) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  const currentQuestion = session.questions[currentIndex];

  if (!currentQuestion) {
    // All questions answered — redirect to report
    sessionStorage.setItem("interview_session_id", String(session.session_id));
    router.push("/interview/report");
    return null;
  }

  const handleRate = async (score: "mastered" | "partial" | "unfamiliar") => {
    await submitAnswer(session.session_id, currentQuestion.id, score);
    setCurrentIndex((prev) => prev + 1);
  };

  return (
    <InterviewQuestion
      point={currentQuestion}
      index={currentIndex}
      total={session.questions.length}
      onRate={handleRate}
    />
  );
}

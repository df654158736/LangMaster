"use client";

import { useState } from "react";

interface CodeBlockProps {
  code: string;
}

export default function CodeBlock({ code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <button
        onClick={handleCopy}
        className="absolute right-3 top-3 rounded bg-gray-700 px-2 py-1 text-xs text-gray-300 hover:bg-gray-600"
      >
        {copied ? "已复制" : "复制"}
      </button>
      <pre className="overflow-x-auto rounded-lg bg-gray-900 p-4 text-sm leading-relaxed text-gray-100">
        <code>{code}</code>
      </pre>
    </div>
  );
}

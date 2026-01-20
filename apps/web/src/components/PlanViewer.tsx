'use client';

import { useRef, useEffect } from 'react';

interface PlanViewerProps {
  html: string;
}

export default function PlanViewer({ html }: PlanViewerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (iframeRef.current && html) {
      // Use srcdoc for security - content is sandboxed
      iframeRef.current.srcdoc = html;
    }
  }, [html]);

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="bg-gray-100 px-4 py-2 border-b flex items-center gap-2">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-400"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
          <div className="w-3 h-3 rounded-full bg-green-400"></div>
        </div>
        <span className="text-sm text-gray-500 ml-2">Kế hoạch học tập của bạn</span>
      </div>
      <iframe
        ref={iframeRef}
        title="Study Plan"
        className="w-full min-h-[600px] border-0"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}

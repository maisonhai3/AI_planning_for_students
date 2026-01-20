'use client';

import { useState } from 'react';
import InputForm from '@/components/InputForm';
import PlanViewer from '@/components/PlanViewer';
import LoadingState from '@/components/LoadingState';
import ActionButtons from '@/components/ActionButtons';

interface GeneratedPlan {
  json: object;
  html: string;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [plan, setPlan] = useState<GeneratedPlan | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (input: string) => {
    setIsLoading(true);
    setError(null);
    setPlan(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/generate/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Có lỗi xảy ra khi tạo kế hoạch');
      }

      setPlan({
        json: data.plan,
        html: data.html,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Có lỗi xảy ra');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = () => {
    // Will implement: track regenerate action + call API again
    console.log('Regenerate clicked');
  };

  const handleSave = async () => {
    // Will implement: save to Firestore
    console.log('Save clicked');
  };

  const handleShare = () => {
    // Will implement: copy share link
    console.log('Share clicked');
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">📚</span>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Student Study Planner
                </h1>
                <p className="text-sm text-gray-500">
                  AI-powered • Gemini 2.5
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {!plan && !isLoading && (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Tạo kế hoạch học tập thông minh
              </h2>
              <p className="text-gray-600">
                Nhập syllabus, to-do list, hoặc mô tả môn học của bạn.
                <br />
                AI sẽ tự động tạo lịch học tối ưu cho bạn.
              </p>
            </div>
            <InputForm onSubmit={handleGenerate} isLoading={isLoading} />
          </div>
        )}

        {isLoading && <LoadingState />}

        {error && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              <p className="font-medium">Lỗi</p>
              <p className="text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm underline hover:no-underline"
              >
                Thử lại
              </button>
            </div>
          </div>
        )}

        {plan && !isLoading && (
          <div className="space-y-6">
            <ActionButtons
              onRegenerate={handleRegenerate}
              onSave={handleSave}
              onShare={handleShare}
            />
            <PlanViewer html={plan.html} />
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t bg-white mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            Made with ❤️ for Vietnamese students • Powered by Gemini 2.5
          </p>
        </div>
      </footer>
    </main>
  );
}

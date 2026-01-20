'use client';

export default function LoadingState() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex flex-col items-center justify-center space-y-6">
          {/* Animated loader */}
          <div className="relative">
            <div className="w-16 h-16 border-4 border-primary-200 rounded-full animate-spin border-t-primary-600"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">📚</span>
            </div>
          </div>

          {/* Loading text */}
          <div className="text-center space-y-2">
            <h3 className="text-lg font-semibold text-gray-900">
              Đang tạo kế hoạch học tập...
            </h3>
            <p className="text-sm text-gray-500">
              AI đang phân tích và tối ưu lịch học cho bạn
            </p>
          </div>

          {/* Progress steps */}
          <div className="w-full max-w-xs space-y-3">
            <LoadingStep step={1} text="Phân tích input" done />
            <LoadingStep step={2} text="Tạo kế hoạch" active />
            <LoadingStep step={3} text="Thiết kế giao diện" />
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingStep({
  step,
  text,
  done,
  active,
}: {
  step: number;
  text: string;
  done?: boolean;
  active?: boolean;
}) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
          done
            ? 'bg-green-500 text-white'
            : active
            ? 'bg-primary-500 text-white animate-pulse'
            : 'bg-gray-200 text-gray-500'
        }`}
      >
        {done ? '✓' : step}
      </div>
      <span
        className={`text-sm ${
          done
            ? 'text-green-600'
            : active
            ? 'text-primary-600 font-medium'
            : 'text-gray-400'
        }`}
      >
        {text}
      </span>
    </div>
  );
}

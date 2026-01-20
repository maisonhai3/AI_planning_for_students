'use client';

interface ActionButtonsProps {
  onRegenerate: () => void;
  onSave: () => void;
  onShare: () => void;
}

export default function ActionButtons({
  onRegenerate,
  onSave,
  onShare,
}: ActionButtonsProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 bg-white rounded-lg shadow p-4">
      <div className="flex items-center gap-2">
        <span className="text-green-500">✓</span>
        <span className="text-sm text-gray-600">Kế hoạch đã được tạo thành công!</span>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={onRegenerate}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors flex items-center gap-2"
        >
          <span>🔄</span>
          Tạo lại
        </button>

        <button
          onClick={onSave}
          className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors flex items-center gap-2"
        >
          <span>💾</span>
          Lưu kế hoạch
        </button>

        <button
          onClick={onShare}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors flex items-center gap-2"
        >
          <span>🔗</span>
          Chia sẻ
        </button>
      </div>
    </div>
  );
}

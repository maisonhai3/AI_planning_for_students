'use client';

import { useState } from 'react';

interface InputFormProps {
  onSubmit: (input: string) => void;
  isLoading: boolean;
}

const EXAMPLE_INPUTS = [
  {
    label: 'Ôn thi đơn giản',
    text: `Tuần sau tôi có bài kiểm tra môn Toán Cao Cấp.
Cần ôn tập 3 chương: Giới hạn, Đạo hàm, Tích phân.
Mỗi ngày tôi có thể học 2 tiếng buổi tối (19h-21h).`,
  },
  {
    label: 'Lịch học phức tạp',
    text: `Em là sinh viên năm 3 ngành CNTT. Học kỳ này em có:
- Đồ án môn học (deadline 15/2)
- Thi cuối kỳ 5 môn (từ 20/2 - 28/2): Mạng máy tính, CSDL, AI, Web, Mobile
- Thực tập công ty part-time (T2, T4, T6 sáng)
- Muốn học thêm AWS để thi chứng chỉ

Em không biết sắp xếp thế nào vì đồ án còn dang dở mà thi cũng gần.
Buổi tối em hay mệt nên chỉ học được nhẹ nhàng thôi.`,
  },
];

export default function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input);
    }
  };

  const handleExampleClick = (text: string) => {
    setInput(text);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Example buttons */}
      <div className="flex flex-wrap gap-2">
        <span className="text-sm text-gray-500">Ví dụ:</span>
        {EXAMPLE_INPUTS.map((example, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handleExampleClick(example.text)}
            className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
          >
            {example.label}
          </button>
        ))}
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Nhập syllabus, to-do list, hoặc mô tả môn học của bạn..."
          className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-400"
          disabled={isLoading}
        />
        <div className="absolute bottom-3 right-3 text-xs text-gray-400">
          {input.length} / 10000
        </div>
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={!input.trim() || isLoading}
        className="w-full py-3 px-6 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Đang tạo kế hoạch...
          </>
        ) : (
          <>
            <span>✨</span>
            Tạo kế hoạch học tập
          </>
        )}
      </button>
    </form>
  );
}

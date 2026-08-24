import { BookOpen } from "lucide-react";

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <BookOpen className="h-12 w-12 text-primary-600 animate-spin mx-auto mb-4" />
        <p className="text-gray-600">Đang tải...</p>
      </div>
    </div>
  );
}

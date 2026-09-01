export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Không tìm thấy</h2>
        <p className="text-gray-600 mb-8">Trang bạn đang tìm kiếm không tồn tại.</p>
        <a
          href="/"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          Về trang chủ
        </a>
      </div>
    </div>
  );
}

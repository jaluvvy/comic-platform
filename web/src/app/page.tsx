import Link from "next/link";
import { BookOpen, TrendingUp, Search } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-primary-50 to-white py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Thư viện Truyện Tranh
            <span className="block text-primary-600">Toàn diện nhất</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Khám phá hàng nghìn đầu truyện từ các NXB hàng đầu. 
            Mua bán, tra cứu thông tin và kết nối với cộng đồng yêu thích truyện tranh.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/comics"
              className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Search className="mr-2 h-5 w-5" />
              Khám phá thư viện
            </Link>
            <Link 
              href="/listings"
              className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            >
              <TrendingUp className="mr-2 h-5 w-5" />
              Xem listings
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BookOpen className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Thư viện đầy đủ</h3>
              <p className="text-gray-600">
                Dữ liệu từ nhiều NXB, cập nhật hàng ngày với thông tin chi tiết về giá, ISBN, tác giả.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Mua bán dễ dàng</h3>
              <p className="text-gray-600">
                Tạo bài đăng bán từ thư viện, tự động tạo mẫu bài cho Facebook hoặc website.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Search className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Tìm kiếm thông minh</h3>
              <p className="text-gray-600">
                Bộ lọc chi tiết theo tên, tác giả, NXB, giá cả, tình trạng sách và nhiều hơn.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

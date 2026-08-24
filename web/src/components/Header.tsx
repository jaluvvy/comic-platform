import Link from "next/link";
import { BookOpen, Search, ShoppingCart } from "lucide-react";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center space-x-2">
          <BookOpen className="h-6 w-6 text-primary-600" />
          <span className="text-xl font-bold text-gray-900">ComicPlatform</span>
        </Link>
        
        <nav className="flex items-center space-x-6">
          <Link 
            href="/comics" 
            className="flex items-center space-x-1 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
          >
            <BookOpen className="h-4 w-4" />
            <span>Thư viện</span>
          </Link>
          <Link 
            href="/listings" 
            className="flex items-center space-x-1 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
          >
            <ShoppingCart className="h-4 w-4" />
            <span>Mua bán</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}

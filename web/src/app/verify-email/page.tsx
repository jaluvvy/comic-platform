"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function VerifyEmailPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const hash = window.location.hash;
        const params = new URLSearchParams(hash.substring(1));
        const accessToken = params.get("access_token");
        const refreshToken = params.get("refresh_token");
        const type = params.get("type");

        if (type === "signup" && accessToken && refreshToken) {
          const { error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          });

          if (error) {
            setStatus("error");
            setMessage("Link xác nhận đã hết hạn hoặc không hợp lệ. Vui lòng đăng ký lại.");
            return;
          }

          setStatus("success");
          setMessage("Email đã được xác nhận thành công! Đang chuyển hướng...");
          setTimeout(() => {
            router.push("/comics");
          }, 2000);
        } else if (type === "recovery") {
          setStatus("success");
          setMessage("Link đặt lại mật khẩu đã được xác nhận.");
        } else {
          setStatus("error");
          setMessage("Link xác nhận không hợp lệ.");
        }
      } catch (e) {
        setStatus("error");
        setMessage("Đã xảy ra lỗi. Vui lòng thử lại.");
      }
    };

    verifyEmail();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Xác nhận email
          </h2>
        </div>

        <div className="rounded-md p-4">
          {status === "loading" && (
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <p className="text-sm text-gray-700">Đang xác nhận email...</p>
            </div>
          )}

          {status === "success" && (
            <div className="rounded-md bg-green-50 p-4">
              <p className="text-sm text-green-800">{message}</p>
            </div>
          )}

          {status === "error" && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{message}</p>
              <div className="mt-4 flex flex-col space-y-2">
                <Link
                  href="/register"
                  className="text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  Đăng ký lại
                </Link>
                <Link
                  href="/login"
                  className="text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  Quay lại đăng nhập
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

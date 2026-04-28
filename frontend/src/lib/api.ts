import type { Booking } from "@/data/mockData";

type RequestOptions = {
  method?: "GET" | "POST";
  body?: unknown;
};

declare global {
  interface Window {
    __ROOM_BOOKING_BOOTSTRAP__?: {
      csrfToken?: string;
      isAuthenticated?: boolean;
      currentUser?: unknown;
      rooms?: unknown[];
      bookings?: Booking[];
    };
  }
}

const csrfToken = () => window.__ROOM_BOOKING_BOOTSTRAP__?.csrfToken || "";

export async function apiRequest<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(url, {
    method: options.method || "GET",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken(),
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "ไม่สามารถเชื่อมต่อระบบได้");
  }
  return data as T;
}

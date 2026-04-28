/// <reference types="vite/client" />

interface Window {
  __ROOM_BOOKING_BOOTSTRAP__?: {
    csrfToken?: string;
    isAuthenticated?: boolean;
    currentUser?: unknown;
    rooms?: unknown[];
    bookings?: import("@/data/mockData").Booking[];
  };
}

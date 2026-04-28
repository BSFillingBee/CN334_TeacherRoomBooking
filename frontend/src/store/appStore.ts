import { create } from "zustand";
import { Booking, currentUser, initialBookings } from "@/data/mockData";
import { apiRequest } from "@/lib/api";

type Role = "staff" | "admin";

interface BookingInput {
  roomId: string;
  date: string;
  startTime: string;
  endTime: string;
  purpose: string;
  attendees?: number;
}

interface AppState {
  bookings: Booking[];
  isAuthenticated: boolean;
  role: Role;
  addBooking: (b: BookingInput) => Promise<Booking>;
  cancelBooking: (id: string) => Promise<void>;
  approveBooking: (id: string) => Promise<void>;
  rejectBooking: (id: string, reason?: string) => Promise<void>;
  login: (role: Role, username?: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const bootstrap = window.__ROOM_BOOKING_BOOTSTRAP__;

const replaceBooking = (bookings: Booking[], updated: Booking) =>
  bookings.map((booking) => (booking.id === updated.id ? updated : booking));

export const useAppStore = create<AppState>((set) => ({
  bookings: initialBookings,
  isAuthenticated: bootstrap?.isAuthenticated ?? true,
  role: currentUser.role,
  addBooking: async (payload) => {
    const { booking } = await apiRequest<{ booking: Booking }>("/api/bookings/", {
      method: "POST",
      body: payload,
    });
    set((state) => ({ bookings: [booking, ...state.bookings] }));
    return booking;
  },
  cancelBooking: async (id) => {
    const { booking } = await apiRequest<{ booking: Booking }>(`/api/bookings/${id}/cancel/`, {
      method: "POST",
    });
    set((state) => ({ bookings: replaceBooking(state.bookings, booking) }));
  },
  approveBooking: async (id) => {
    const { booking } = await apiRequest<{ booking: Booking }>(`/api/bookings/${id}/review/`, {
      method: "POST",
      body: { action: "approve" },
    });
    set((state) => ({ bookings: replaceBooking(state.bookings, booking) }));
  },
  rejectBooking: async (id, reason = "") => {
    const { booking } = await apiRequest<{ booking: Booking }>(`/api/bookings/${id}/review/`, {
      method: "POST",
      body: { action: "reject", reason },
    });
    set((state) => ({ bookings: replaceBooking(state.bookings, booking) }));
  },
  login: async (role, username, password) => {
    if (username && password) {
      const data = await apiRequest<{
        isAuthenticated: boolean;
        currentUser: typeof currentUser;
        bookings: Booking[];
      }>("/api/login/", {
        method: "POST",
        body: { username, password },
      });
      window.__ROOM_BOOKING_BOOTSTRAP__ = {
        ...window.__ROOM_BOOKING_BOOTSTRAP__,
        ...data,
      };
      set({
        isAuthenticated: data.isAuthenticated,
        role: data.currentUser?.role || role,
        bookings: data.bookings,
      });
      return;
    }

    set({ isAuthenticated: true, role });
  },
  logout: async () => {
    await apiRequest("/api/logout/", { method: "POST" });
    set({ isAuthenticated: false, role: "staff", bookings: [] });
  },
}));

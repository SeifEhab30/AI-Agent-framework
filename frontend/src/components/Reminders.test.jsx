import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Reminders from "./Reminders";
import { remindersApi } from "../api";

vi.mock("../api", () => ({
  remindersApi: {
    list: vi.fn(),
    create: vi.fn(),
    markDone: vi.fn(),
    delete: vi.fn(),
  },
}));

describe("Reminders", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from remindersApi.list()", async () => {
    remindersApi.list.mockResolvedValue([
      { id: "1", message: "Buy milk", due_at: "2026-09-01T10:00:00+00:00", done: false },
    ]);

    render(<Reminders />);

    expect(await screen.findByText("Buy milk")).toBeInTheDocument();
  });

  it("creates a reminder and reloads the list", async () => {
    remindersApi.list.mockResolvedValueOnce([]).mockResolvedValueOnce([
      { id: "2", message: "Call back", due_at: "2026-09-02T09:00:00+00:00", done: false },
    ]);
    remindersApi.create.mockResolvedValue({
      id: "2",
      message: "Call back",
      due_at: "2026-09-02T09:00:00+00:00",
      done: false,
    });

    const user = userEvent.setup();
    render(<Reminders />);

    await waitFor(() => expect(remindersApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("Message"), "Call back");
    await user.type(screen.getByLabelText("Due date"), "2026-09-02T09:00");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(remindersApi.create).toHaveBeenCalledWith("Call back", "2026-09-02T09:00");
    expect(await screen.findByText("Call back")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    remindersApi.list.mockResolvedValue([]);
    remindersApi.create.mockRejectedValue(new Error("due_at must be in the future"));

    const user = userEvent.setup();
    render(<Reminders />);

    await waitFor(() => expect(remindersApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("Message"), "Call back");
    await user.type(screen.getByLabelText("Due date"), "2020-01-01T09:00");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("due_at must be in the future")).toBeInTheDocument();
  });
});

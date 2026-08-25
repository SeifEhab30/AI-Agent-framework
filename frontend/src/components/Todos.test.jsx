import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Todos from "./Todos";
import { todosApi } from "../api";

vi.mock("../api", () => ({
  todosApi: {
    list: vi.fn(),
    create: vi.fn(),
    toggle: vi.fn(),
  },
}));

describe("Todos", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from todosApi.list()", async () => {
    todosApi.list.mockResolvedValue([{ id: "1", title: "buy milk", done: false }]);

    render(<Todos />);

    expect(await screen.findByText("buy milk")).toBeInTheDocument();
  });

  it("creates a todo and reloads the list", async () => {
    todosApi.list
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: "2", title: "New Todo", done: false }]);
    todosApi.create.mockResolvedValue({ id: "2", title: "New Todo", done: false });

    const user = userEvent.setup();
    render(<Todos />);

    await waitFor(() => expect(todosApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("New todo title"), "New Todo");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(todosApi.create).toHaveBeenCalledWith("New Todo");
    expect(await screen.findByText("New Todo")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    todosApi.list.mockResolvedValue([]);
    todosApi.create.mockRejectedValue(new Error("title must not be empty"));

    const user = userEvent.setup();
    render(<Todos />);

    await waitFor(() => expect(todosApi.list).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("title must not be empty")).toBeInTheDocument();
  });
});

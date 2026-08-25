import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Notes from "./Notes";
import { notesApi } from "../api";

vi.mock("../api", () => ({
  notesApi: {
    list: vi.fn(),
    create: vi.fn(),
    updateBody: vi.fn(),
  },
}));

describe("Notes", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from notesApi.list()", async () => {
    notesApi.list.mockResolvedValue([{ id: "1", title: "groceries", body: "milk" }]);

    render(<Notes />);

    expect(await screen.findByText("groceries")).toBeInTheDocument();
  });

  it("creates a note and reloads the list", async () => {
    notesApi.list
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: "2", title: "New Note", body: "" }]);
    notesApi.create.mockResolvedValue({ id: "2", title: "New Note", body: "" });

    const user = userEvent.setup();
    render(<Notes />);

    await waitFor(() => expect(notesApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("New note title"), "New Note");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(notesApi.create).toHaveBeenCalledWith("New Note", "");
    expect(await screen.findByText("New Note")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    notesApi.list.mockResolvedValue([]);
    notesApi.create.mockRejectedValue(new Error("title must not be empty"));

    const user = userEvent.setup();
    render(<Notes />);

    await waitFor(() => expect(notesApi.list).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("title must not be empty")).toBeInTheDocument();
  });
});

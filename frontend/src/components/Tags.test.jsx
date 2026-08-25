import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Tags from "./Tags";
import { tagsApi } from "../api";

vi.mock("../api", () => ({
  tagsApi: {
    list: vi.fn(),
    create: vi.fn(),
    search: vi.fn(),
  },
}));

describe("Tags", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from tagsApi.list()", async () => {
    tagsApi.list.mockResolvedValue([{ id: "1", name: "urgent" }]);

    render(<Tags />);

    expect(await screen.findByText("urgent")).toBeInTheDocument();
  });

  it("creates a tag and reloads the list", async () => {
    tagsApi.list.mockResolvedValueOnce([]).mockResolvedValueOnce([{ id: "2", name: "backlog" }]);
    tagsApi.create.mockResolvedValue({ id: "2", name: "backlog" });

    const user = userEvent.setup();
    render(<Tags />);

    await waitFor(() => expect(tagsApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("Name"), "backlog");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(tagsApi.create).toHaveBeenCalledWith("backlog");
    expect(await screen.findByText("backlog")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    tagsApi.list.mockResolvedValue([]);
    tagsApi.create.mockRejectedValue(new Error("name must not be empty"));

    const user = userEvent.setup();
    render(<Tags />);

    await waitFor(() => expect(tagsApi.list).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("name must not be empty")).toBeInTheDocument();
  });
});

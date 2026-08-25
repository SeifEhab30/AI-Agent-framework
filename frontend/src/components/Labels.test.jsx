import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Labels from "./Labels";
import { labelsApi } from "../api";

vi.mock("../api", () => ({
  labelsApi: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
    search: vi.fn(),
  },
}));

describe("Labels", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from labelsApi.list()", async () => {
    labelsApi.list.mockResolvedValue([{ id: "1", name: "urgent", color: "#FF0000" }]);

    render(<Labels />);

    expect(await screen.findByText("urgent")).toBeInTheDocument();
  });

  it("creates a label and reloads the list", async () => {
    labelsApi.list
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: "2", name: "backlog", color: "#00FF00" }]);
    labelsApi.create.mockResolvedValue({ id: "2", name: "backlog", color: "#00FF00" });

    const user = userEvent.setup();
    render(<Labels />);

    await waitFor(() => expect(labelsApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("Name"), "backlog");
    await user.type(screen.getByPlaceholderText("#RRGGBB"), "#00FF00");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(labelsApi.create).toHaveBeenCalledWith("backlog", "#00FF00");
    expect(await screen.findByText("backlog")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    labelsApi.list.mockResolvedValue([]);
    labelsApi.create.mockRejectedValue(new Error("color must be in #RRGGBB hex format"));

    const user = userEvent.setup();
    render(<Labels />);

    await waitFor(() => expect(labelsApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("Name"), "backlog");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("color must be in #RRGGBB hex format")).toBeInTheDocument();
  });
});

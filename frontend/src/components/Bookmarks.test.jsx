import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Bookmarks from "./Bookmarks";
import { bookmarksApi } from "../api";

vi.mock("../api", () => ({
  bookmarksApi: {
    list: vi.fn(),
    create: vi.fn(),
    rename: vi.fn(),
  },
}));

describe("Bookmarks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from bookmarksApi.list()", async () => {
    bookmarksApi.list.mockResolvedValue([
      { id: "1", url: "https://example.com", title: "Example Docs" },
    ]);

    render(<Bookmarks />);

    expect(await screen.findByText("Example Docs")).toBeInTheDocument();
  });

  it("creates a bookmark and reloads the list", async () => {
    bookmarksApi.list.mockResolvedValueOnce([]).mockResolvedValueOnce([
      { id: "2", url: "https://example.com", title: "New Bookmark" },
    ]);
    bookmarksApi.create.mockResolvedValue({
      id: "2",
      url: "https://example.com",
      title: "New Bookmark",
    });

    const user = userEvent.setup();
    render(<Bookmarks />);

    await waitFor(() => expect(bookmarksApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("URL"), "https://example.com");
    await user.type(screen.getByPlaceholderText("Title"), "New Bookmark");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(bookmarksApi.create).toHaveBeenCalledWith("https://example.com", "New Bookmark");
    expect(await screen.findByText("New Bookmark")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    bookmarksApi.list.mockResolvedValue([]);
    bookmarksApi.create.mockRejectedValue(new Error("title must not be empty"));

    const user = userEvent.setup();
    render(<Bookmarks />);

    await waitFor(() => expect(bookmarksApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("URL"), "https://example.com");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("title must not be empty")).toBeInTheDocument();
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Widgets from "./Widgets";
import { widgetsApi } from "../api";

vi.mock("../api", () => ({
  widgetsApi: {
    list: vi.fn(),
    create: vi.fn(),
    setValue: vi.fn(),
  },
}));

describe("Widgets", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the list from widgetsApi.list()", async () => {
    widgetsApi.list.mockResolvedValue([{ id: "1", label: "Counter", value: 3 }]);

    render(<Widgets />);

    expect(await screen.findByText("Counter")).toBeInTheDocument();
  });

  it("creates a widget and reloads the list", async () => {
    widgetsApi.list
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: "2", label: "New Widget", value: 0 }]);
    widgetsApi.create.mockResolvedValue({ id: "2", label: "New Widget", value: 0 });

    const user = userEvent.setup();
    render(<Widgets />);

    await waitFor(() => expect(widgetsApi.list).toHaveBeenCalledTimes(1));

    await user.type(screen.getByPlaceholderText("Label"), "New Widget");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(widgetsApi.create).toHaveBeenCalledWith("New Widget", 0);
    expect(await screen.findByText("New Widget")).toBeInTheDocument();
  });

  it("shows an error message when create fails", async () => {
    widgetsApi.list.mockResolvedValue([]);
    widgetsApi.create.mockRejectedValue(new Error("label must not be empty"));

    const user = userEvent.setup();
    render(<Widgets />);

    await waitFor(() => expect(widgetsApi.list).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("label must not be empty")).toBeInTheDocument();
  });
});

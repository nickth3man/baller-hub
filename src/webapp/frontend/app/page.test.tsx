import { expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Page from "./page";

// Mock child components to avoid data fetching issues in unit test
vi.mock("@/(components)/stats/TodaysGames", () => ({
  TodaysGames: () => <div data-testid="todays-games">Todays Games</div>,
}));

vi.mock("@/(components)/stats/LeagueLeaders", () => ({
  LeagueLeaders: () => <div data-testid="league-leaders">League Leaders</div>,
}));

vi.mock("@/(components)/stats/StandingsPreview", () => ({
  StandingsPreview: () => (
    <div data-testid="standings-preview">Standings Preview</div>
  ),
}));

test("Page renders main heading", () => {
  render(<Page />);
  expect(
    screen.getByRole("heading", { level: 1, name: /Baller Hub/i })
  ).toBeDefined();
  expect(screen.getByTestId("todays-games")).toBeDefined();
});

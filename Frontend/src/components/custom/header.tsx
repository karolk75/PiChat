import { ThemeToggle } from "./theme-toggle";

export const Header = () => {
  return (
    <>
      <header className="flex items-center justify-between px-2 sm:px-4 py-2 bg-background text-black dark:text-white w-full">
        <div className="flex-1 text-center sm:text-left">
          <h1 className="text-lg font-semibold">PiChat</h1>
        </div>
        <div className="flex items-center space-x-1 sm:space-x-2">
          <ThemeToggle />
        </div>
      </header>
    </>
  );
};
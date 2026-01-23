import { Header } from "./Header";
import { Footer } from "./Footer";

interface PageLayoutProps {
  children: React.ReactNode;
  containerClassName?: string;
}

export function PageLayout({ children, containerClassName = "container mx-auto flex-1 px-4 py-6" }: PageLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className={containerClassName}>
        {children}
      </main>
      <Footer />
    </div>
  );
}

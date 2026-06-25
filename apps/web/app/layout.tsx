import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Material Data Intelligence",
  description: "Materials analysis workspace shell"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

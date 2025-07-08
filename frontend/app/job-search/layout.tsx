"use client"

import { ThemeProvider } from "../../components/theme-provider"
 
export default function JobSearchLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
    >
      {children}
    </ThemeProvider>
  )
}

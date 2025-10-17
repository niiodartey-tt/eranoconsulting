import './globals.css'

export const metadata = {
  title: 'Erano Consulting',
  description: 'Accounting and Advisory Firm',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

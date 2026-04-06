import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Antigravity VK Manager Pro',
  description: 'Профессиональная система автоматизации и контент-менеджмента VK',
}

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body className={`${inter.className} bg-[#0a0a1a] text-white min-h-screen`}>
        {children}
      </body>
    </html>
  )
}

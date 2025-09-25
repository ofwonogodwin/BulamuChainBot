import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/contexts/AuthContext';
import { LanguageProvider } from '@/contexts/LanguageContext';

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "BulamuChainBot - AI Health Assistant",
  description: "AI-powered healthcare assistant for rural Uganda with blockchain-verified medical records",
  keywords: ["healthcare", "AI", "blockchain", "Uganda", "medical", "telemedicine"],
  authors: [{ name: "BulamuChainBot Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased bg-blue-50 min-h-screen font-sans`}>
        <AuthProvider>
          <LanguageProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#f8fafc',
                  color: '#1e293b',
                  border: '1px solid #cbd5e1',
                },
              }}
            />
          </LanguageProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

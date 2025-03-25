import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { PsuuProvider } from '@/contexts/PsuuContext';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <PsuuProvider>
      <Component {...pageProps} />
    </PsuuProvider>
  );
}

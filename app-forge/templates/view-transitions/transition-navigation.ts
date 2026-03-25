// lib/transition-navigation.ts
// Navigation helper that wraps router.push with View Transitions API.

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

type TransitionDirection = 'push' | 'pop' | 'fade' | 'cover' | 'reveal';

export function useTransitionNavigation() {
  const router = useRouter();

  const navigate = useCallback(
    (url: string, direction: TransitionDirection = 'push') => {
      if (
        !document.startViewTransition ||
        window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ) {
        router.push(url);
        return;
      }

      document.documentElement.dataset.transitionDirection = direction;
      const transition = document.startViewTransition(() => {
        router.push(url);
      });

      transition.finished.then(() => {
        delete document.documentElement.dataset.transitionDirection;
      });
    },
    [router]
  );

  const goBack = useCallback(() => {
    if (
      !document.startViewTransition ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      router.back();
      return;
    }

    document.documentElement.dataset.transitionDirection = 'pop';
    const transition = document.startViewTransition(() => {
      router.back();
    });

    transition.finished.then(() => {
      delete document.documentElement.dataset.transitionDirection;
    });
  }, [router]);

  return { navigate, goBack };
}

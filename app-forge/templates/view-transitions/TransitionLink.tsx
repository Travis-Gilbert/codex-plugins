// components/TransitionLink.tsx
// Next.js Link wrapper with directional view transition support.
'use client';

import { type ComponentPropsWithoutRef } from 'react';
import { useTransitionNavigation } from '../lib/transition-navigation';

type TransitionDirection = 'push' | 'pop' | 'fade' | 'cover' | 'reveal';

interface TransitionLinkProps extends Omit<ComponentPropsWithoutRef<'a'>, 'href'> {
  href: string;
  direction?: TransitionDirection;
}

export function TransitionLink({
  href,
  direction = 'push',
  children,
  ...props
}: TransitionLinkProps) {
  const { navigate } = useTransitionNavigation();

  return (
    <a
      href={href}
      onClick={(e) => {
        e.preventDefault();
        navigate(href, direction);
      }}
      {...props}
    >
      {children}
    </a>
  );
}

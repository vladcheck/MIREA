import type { BaseHTMLAttributes, PropsWithChildren } from 'react';
import cn from '@/shared/utils/cn';

export default function Header({
	children,
	...props
}: PropsWithChildren & BaseHTMLAttributes<HTMLDivElement>) {
	return (
		<header {...props} className={cn('header', props.className)}>
			{children}
		</header>
	);
}

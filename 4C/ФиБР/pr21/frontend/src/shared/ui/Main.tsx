import type { BaseHTMLAttributes, PropsWithChildren } from 'react';
import cn from '@/shared/utils/cn';

export default function Main({
	children,
	...props
}: PropsWithChildren & BaseHTMLAttributes<HTMLDivElement>) {
	return (
		<main {...props} className={cn('main w-dvw min-h-dvh', props.className)}>
			{children}
		</main>
	);
}

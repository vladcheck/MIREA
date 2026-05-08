import type { PropsWithChildren } from 'react';
import cn from '@/shared/utils/cn';

interface InputWrapperProps extends PropsWithChildren {
	className?: string;
}

export default function InputWrapper({
	children,
	className,
}: InputWrapperProps) {
	return (
		<div className={cn('input-wrapper relative w-full', className)}>
			{children}
		</div>
	);
}

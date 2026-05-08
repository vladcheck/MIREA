import type { BaseHTMLAttributes, PropsWithChildren } from 'react';
import cn from '@/shared/utils/cn';

export default function FlexContainer({
	children,
	flexDir = 'row',
	justify = 'start',
	align = 'start',
	...props
}: PropsWithChildren &
	BaseHTMLAttributes<HTMLDivElement> & {
		flexDir?: 'row' | 'col';
		justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
		align?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
	}) {
	return (
		<div
			{...props}
			className={cn(
				`flex flex-${flexDir} justify-${justify} items-${align}`,
				props.className,
			)}
		>
			{children}
		</div>
	);
}

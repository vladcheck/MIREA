import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';
import cn from '@/shared/utils/cn';

type ButtonVariant =
	| 'primary'
	| 'secondary'
	| 'glass'
	| 'danger'
	| 'ghost'
	| 'ghost-primary'
	| 'secondary-danger'
	| 'secondary-success'
	| 'outline'
	| 'none';

type ButtonSize = 'sm' | 'md' | 'lg' | 'xl' | 'icon';
type ButtonRounded = 'md' | 'lg' | 'xl' | '2xl' | 'full';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: ButtonVariant;
	size?: ButtonSize;
	rounded?: ButtonRounded;
	fullWidth?: boolean;
	pointerEvents?: 'auto' | 'none' | 'inherit';
}

export default function Button({
	onClick,
	children,
	className,
	variant = 'secondary',
	size = 'md',
	rounded = 'xl',
	fullWidth = false,
	pointerEvents = 'inherit',
	...props
}: PropsWithChildren<ButtonProps>) {
	const variants: Record<ButtonVariant, string> = {
		primary:
			'bg-primary text-white shadow-xl shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-0.5 active:scale-95',
		secondary:
			'bg-slate-100 dark:bg-slate-800 text-text-color hover:bg-slate-200 dark:hover:bg-slate-700 active:scale-95',
		'secondary-danger':
			'bg-slate-100 dark:bg-slate-800 text-text-color hover:text-red-500 hover:bg-red-500/10 active:scale-95',
		'secondary-success':
			'bg-slate-100 dark:bg-slate-800 text-text-color hover:text-green-500 hover:bg-green-500/10 active:scale-95',
		glass:
			'bg-white/20 dark:bg-dark-surface/20 backdrop-blur-xl border border-white/20 dark:border-white/5 text-text-color shadow-glass hover:bg-white/40 dark:hover:bg-dark-surface/40 active:scale-95',
		danger:
			'bg-red-500 text-white shadow-xl shadow-red-500/20 hover:shadow-red-500/40 hover:-translate-y-0.5 active:scale-95',
		ghost:
			'bg-transparent text-text-color hover:bg-slate-100 dark:hover:bg-slate-800 active:scale-95',
		'ghost-primary':
			'bg-transparent text-primary hover:bg-primary/10 hover:underline underline-offset-4 active:scale-95',
		outline:
			'bg-transparent border-2 border-primary text-primary hover:bg-primary/10 active:scale-95',
		none: '',
	};

	const sizes: Record<ButtonSize, string> = {
		sm: 'px-3 py-1.5 text-xs',
		md: 'px-5 py-2.5 text-sm',
		lg: 'px-8 py-4 text-base',
		xl: 'px-10 py-5 text-lg',
		icon: 'w-12 h-12 flex items-center justify-center p-0',
	};

	const roundedMap: Record<ButtonRounded, string> = {
		md: 'rounded-md',
		lg: 'rounded-lg',
		xl: 'rounded-xl',
		'2xl': 'rounded-2xl',
		full: 'rounded-full',
	};

	const pointerEventsMap: Record<
		NonNullable<ButtonProps['pointerEvents']>,
		string
	> = {
		auto: 'pointer-events-auto',
		none: 'pointer-events-none',
		inherit: '',
	};

	const baseClasses =
		variant === 'none'
			? ''
			: 'font-bold transition-all duration-300 select-none flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed';

	return (
		<button
			type="button"
			onClick={onClick}
			className={cn(
				baseClasses,
				variants[variant],
				sizes[size],
				roundedMap[rounded],
				pointerEventsMap[pointerEvents],
				fullWidth ? 'w-full' : '',
				className,
			)}
			{...props}
		>
			{children}
		</button>
	);
}

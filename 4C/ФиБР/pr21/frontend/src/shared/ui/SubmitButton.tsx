import type { MouseEvent, ReactNode, SyntheticEvent } from 'react';
import Button from '@/shared/ui/Button';

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

interface SubmitButtonProps {
	children?: ReactNode;
	formId: string;
	onClick?: (e?: SyntheticEvent) => void;
	variant?: ButtonVariant;
	size?: ButtonSize;
	rounded?: ButtonRounded;
	fullWidth?: boolean;
	className?: string;
}

export default function SubmitButton({
	children,
	formId,
	onClick,
	variant = 'primary',
	size = 'lg',
	rounded = '2xl',
	fullWidth = true,
	className,
}: SubmitButtonProps) {
	return (
		<Button
			form={formId}
			type="submit"
			onClick={(e: MouseEvent<HTMLButtonElement>) => {
				onClick?.(e);
			}}
			variant={variant}
			size={size}
			rounded={rounded}
			fullWidth={fullWidth}
			className={className}
		>
			{children}
		</Button>
	);
}

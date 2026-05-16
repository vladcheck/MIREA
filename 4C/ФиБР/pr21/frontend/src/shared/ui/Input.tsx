import type { InputHTMLAttributes } from 'react';
import cn from '@/shared/utils/cn';
import InputWrapper from './InputWrapper';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
	error?: string;
}

export default function Input({
	value,
	onChange,
	type = 'text',
	className,
	error,
	...props
}: InputProps) {
	return (
		<InputWrapper className="w-full">
			<div className="w-full">
				<input
					type={type}
					value={value}
					onChange={onChange}
					className={cn(
						'input-field block w-full px-4 py-3 rounded-xl border outline-none transition-all',
						error
							? 'border-destructive focus:ring-2 focus:ring-destructive/20 border-2'
							: 'border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
						className,
					)}
					{...props}
				/>
				{error && (
					<p className="text-destructive text-[10px] sm:text-xs font-bold mt-1.5 ml-1 animate-in fade-in slide-in-from-top-1 duration-200">
						{error}
					</p>
				)}
			</div>
		</InputWrapper>
	);
}

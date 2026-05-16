import type { DetailedHTMLProps, InputHTMLAttributes } from 'react';
import cn from '@/shared/utils/cn';
import InputWrapper from './InputWrapper';

export default function Textarea({
	value,
	onChange,
	type = 'text',
	...props
}: DetailedHTMLProps<
	InputHTMLAttributes<HTMLTextAreaElement>,
	HTMLTextAreaElement
>) {
	return (
		<InputWrapper>
			<textarea
				value={value}
				onChange={onChange}
				className={cn(
					'border border-black rounded-sm px-2 py-1',
					props.className,
				)}
				{...props}
			/>
		</InputWrapper>
	);
}

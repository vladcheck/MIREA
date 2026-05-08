import type { InputHTMLAttributes } from 'react';
import Input from './Input';

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
	error?: string;
}

export default function TextInput({
	value,
	onChange,
	error,
	...props
}: TextInputProps) {
	return (
		<Input
			{...props}
			type="text"
			value={value}
			onChange={onChange}
			error={error}
		/>
	);
}

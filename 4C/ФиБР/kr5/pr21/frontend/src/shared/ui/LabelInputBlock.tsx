import type { PropsWithChildren } from 'react';

export default function LabelInputBlock({
	children,
	htmlFor,
	label,
}: PropsWithChildren & { label: string; htmlFor: string }) {
	return (
		<div className="flex flex-col">
			<label htmlFor={htmlFor}>{label}</label>
			{children}
		</div>
	);
}

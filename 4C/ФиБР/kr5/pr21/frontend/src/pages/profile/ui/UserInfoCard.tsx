import FlexContainer from '@/shared/ui/FlexContainer';

export default function UserInfoCard({
	label,
	value,
}: {
	label: string;
	value: string | boolean | number;
}) {
	return (
		<FlexContainer
			justify="between"
			align="end"
			className="py-2 px-4 gap-2 shadow-xs/10 rounded-xs min-w-[clamp(200px,50dvw,600px)]"
		>
			<h4>{label}</h4>
			<span className="text-[1.2rem]">{value}</span>
		</FlexContainer>
	);
}

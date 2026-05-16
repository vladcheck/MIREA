import useHistory from '@/shared/hooks/useHistory';
import Button from '@/shared/ui/Button';
import FlexContainer from '@/shared/ui/FlexContainer';

export default function ProtectedRouteError({ reason }: { reason: string }) {
	const history = useHistory();

	return (
		<FlexContainer
			flexDir="col"
			justify="center"
			align="center"
			className="gap-6"
		>
			<h1 className="text-3xl">Доступ к этой странице запрещен.</h1>
			<p className="text-2xl">
				Причина: <b>{reason}</b>
			</p>
			<Button
				onClick={() => {
					history?.back();
				}}
			>
				Пожалуйста, вернитесь назад.
			</Button>
		</FlexContainer>
	);
}

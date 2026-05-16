import Button from '@/shared/ui/Button';
import FlexContainer from '@/shared/ui/FlexContainer';

export default function AccountActions({
	onLogOut,
	onDeleteAccount,
}: {
	onLogOut: () => void;
	onDeleteAccount: () => void;
}) {
	return (
		<FlexContainer className="gap-4">
			<Button onClick={onLogOut} variant="secondary" size="lg" rounded="xl">
				Выйти
			</Button>
			<Button onClick={onDeleteAccount} variant="danger" size="lg" rounded="xl">
				Удалить аккаунт
			</Button>
		</FlexContainer>
	);
}

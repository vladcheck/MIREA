import { CircleHelp } from 'lucide-react';
import { Link } from 'react-router';
import FlexContainer from '@/shared/ui/FlexContainer';

export default function NotFoundPage() {
	return (
		<FlexContainer
			flexDir="col"
			justify="center"
			align="center"
			className="gap-6"
		>
			<span className="text-4xl">404</span>
			<CircleHelp size={64} className="mx-auto mb-6 text-primary opacity-50" />
			<h1 className="text-2xl">{'Такой страницы не существует'}</h1>
			<Link to={'/shop'}>Перейти на главную страницу</Link>
		</FlexContainer>
	);
}

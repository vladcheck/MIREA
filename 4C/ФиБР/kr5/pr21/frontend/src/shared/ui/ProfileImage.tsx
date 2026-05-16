import { Link } from 'react-router';

export default function ProfileImage({
	to,
	src,
	alt,
}: {
	to: string;
	src?: string;
	alt?: string;
}) {
	return (
		<Link to={to} className="hover:cursor-pointer">
			<div className="aspect-square w-8 h-8 rounded-full bg-gray-200 overflow-clip">
				<img src={src} alt={alt} className="aspect-square" />
			</div>
		</Link>
	);
}

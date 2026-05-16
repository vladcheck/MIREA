import type { Product } from '@root-shared/types/Product';
import { Link } from 'react-router';
import Button from '@/shared/ui/Button';
import FlexContainer from '@/shared/ui/FlexContainer.tsx';
import Price from '@/shared/ui/Price.tsx';

interface CatalogueProductCardProps extends Product {
	onAddToCart?: (e: React.MouseEvent) => void;
}

export default function CatalogueProductCard({
	onAddToCart,
	...p
}: CatalogueProductCardProps) {
	const imageUrl = p.images?.[0]
		? p.images[0].startsWith('http')
			? p.images[0]
			: `http://localhost:3005/images/products${p.images[0].replace('/images/products', '')}`
		: '/images/placeholder.webp';

	return (
		<Link to={`/products/${p.id}`} className="block group animate-slide-up">
			<FlexContainer
				flexDir="col"
				className="glass-card h-full overflow-hidden p-0 gap-0"
			>
				<div className="relative aspect-square overflow-hidden bg-slate-100 dark:bg-slate-800">
					<img
						src={imageUrl}
						alt={p.title}
						className="w-full h-full object-cover transition-all duration-700 group-hover:scale-110"
					/>
					{/* Gradient Overlay */}
					<div className="absolute inset-x-0 bottom-0 h-1/2 bg-linear-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

					<div className="absolute top-4 right-4 z-10">
						<span className="text-[10px] font-black uppercase tracking-widest bg-primary text-white px-3 py-1.5 rounded-full shadow-lg">
							{p.category}
						</span>
					</div>
				</div>

				<div className="p-6 space-y-4">
					<h3 className="text-lg font-black text-text-color line-clamp-1 group-hover:text-primary transition-colors">
						{p.title}
					</h3>

					<div className="flex items-center justify-between">
						<Price className="text-xl font-black text-text-color">
							{p.price}
						</Price>
						<Button
							onClick={(e) => {
								e.preventDefault();
								onAddToCart?.(e);
							}}
							variant="secondary"
							size="icon"
							rounded="xl"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="20"
								height="20"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								strokeWidth="2.5"
								strokeLinecap="round"
								strokeLinejoin="round"
							>
								<circle cx="8" cy="21" r="1" />
								<circle cx="19" cy="21" r="1" />
								<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
							</svg>
						</Button>
					</div>
				</div>
			</FlexContainer>
		</Link>
	);
}

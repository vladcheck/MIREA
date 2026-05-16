import type { Product } from '@root-shared/types/Product';
import { ImageOff, ShoppingCart, Zap } from 'lucide-react';
import Button from '@/shared/ui/Button';
import Price from '@/shared/ui/Price';

export default function ProductCardPreview({
	...p
}: Omit<Product, 'id' | 'author_id'>) {
	const hasTitle = p.title.trim().length > 0;
	const hasDescription = p.description && p.description.trim().length > 0;

	return (
		<div className="glass-panel overflow-hidden shadow-premium">
			{/* Image placeholder */}
			<div className="w-full h-52 bg-surface-hover flex items-center justify-center border-b border-border-color/40">
				<div className="flex flex-col items-center gap-2 text-text-muted opacity-40">
					<ImageOff size={36} />
					<span className="text-xs font-medium">Фото товара</span>
				</div>
			</div>

			{/* Content */}
			<div className="p-6 flex flex-col gap-4">
				<div className="flex items-start justify-between gap-4">
					<div className="flex-1 min-w-0">
						<span className="text-xs font-black uppercase tracking-widest text-primary bg-primary/10 px-2.5 py-1 rounded-full">
							{p.category}
						</span>
						<h2
							className={`mt-3 text-xl font-black leading-tight tracking-tight ${!hasTitle ? 'text-text-muted italic opacity-40' : 'text-text-color'}`}
						>
							{hasTitle ? p.title : 'Название товара'}
						</h2>
					</div>
					<Price className="text-2xl font-black text-primary shrink-0">
						{p.price}
					</Price>
				</div>

				<p
					className={`text-sm leading-relaxed line-clamp-3 ${!hasDescription ? 'text-text-muted italic opacity-40' : 'text-text-muted'}`}
				>
					{hasDescription
						? p.description
						: 'Здесь появится описание вашего товара...'}
				</p>

				<div className="flex gap-3 pt-2">
					<Button variant="primary" size="md" rounded="xl" fullWidth>
						<ShoppingCart size={16} />В корзину
					</Button>
					<Button variant="secondary" size="md" rounded="xl">
						<Zap size={16} />
					</Button>
				</div>
			</div>
		</div>
	);
}

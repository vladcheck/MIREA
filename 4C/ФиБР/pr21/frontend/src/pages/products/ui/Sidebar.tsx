import type { Dispatch, SetStateAction } from 'react';
import FlexContainer from '@/shared/ui/FlexContainer';
import { FILTER_CONFIG } from '../const';
import type { Filters } from '../types';

export default function Sidebar({
	filters,
	setFilters,
}: {
	filters: Filters;
	setFilters: Dispatch<SetStateAction<Filters>>;
}) {
	return (
		<aside className="glass-panel p-6 flex flex-col w-72 h-min gap-6 animate-slide-up">
			<div className="flex items-center gap-2 pb-4 border-b border-border-color/50">
				<span className="text-xl">⚖️</span>
				<h3 className="font-bold text-lg">Фильтры</h3>
			</div>

			<FlexContainer flexDir="col" className="gap-6">
				<div className="flex flex-col gap-3">
					<div className="flex justify-between items-center">
						<label
							htmlFor="min-price"
							className="text-sm font-bold text-text-muted"
						>
							Мин. цена
						</label>
						<span className="text-xs font-black px-2 py-1 bg-primary/10 text-primary rounded-md">
							{filters.price.min} ₽
						</span>
					</div>
					<input
						type="range"
						name="min-price"
						id="min-price"
						className="w-full accent-primary cursor-pointer h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none"
						value={filters.price.min}
						onChange={(e) =>
							setFilters({
								...filters,
								price: { ...filters.price, min: parseInt(e.target.value, 10) },
							})
						}
						min={FILTER_CONFIG.price.min}
						max={filters.price.max}
						step={FILTER_CONFIG.price.step}
					/>
				</div>

				<div className="flex flex-col gap-3">
					<div className="flex justify-between items-center">
						<label
							htmlFor="max-price"
							className="text-sm font-bold text-text-muted"
						>
							Макс. цена
						</label>
						<span className="text-xs font-black px-2 py-1 bg-primary/10 text-primary rounded-md">
							{filters.price.max} ₽
						</span>
					</div>
					<input
						type="range"
						name="max-price"
						id="max-price"
						className="w-full accent-primary cursor-pointer h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none"
						value={filters.price.max}
						onChange={(e) =>
							setFilters({
								...filters,
								price: { ...filters.price, max: parseInt(e.target.value, 10) },
							})
						}
						min={filters.price.min}
						max={FILTER_CONFIG.price.max}
						step={FILTER_CONFIG.price.step}
					/>
				</div>
			</FlexContainer>

			<button
				type="button"
				className="mt-4 text-xs font-bold text-primary hover:text-primary-hover underline underline-offset-4 transition-colors text-left"
				onClick={() =>
					setFilters({
						...filters,
						price: {
							min: FILTER_CONFIG.price.min,
							max: FILTER_CONFIG.price.max,
						},
					})
				}
			>
				Сбросить фильтры
			</button>
		</aside>
	);
}

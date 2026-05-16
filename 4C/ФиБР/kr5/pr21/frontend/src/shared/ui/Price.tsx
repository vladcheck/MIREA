import type { PropsWithChildren } from 'react';
import cn from '@/shared/utils/cn';

type SupportedCurrencies = 'RUB';

const currencyNameToCurrencySumbolMap = new Map<SupportedCurrencies, string>();
currencyNameToCurrencySumbolMap.set('RUB', '₽');

function getCurrencySymbolFromCurrencyName(
	currency: SupportedCurrencies,
): string {
	return currencyNameToCurrencySumbolMap.get(currency) || 'CURRENCY_NOT_FOUND';
}

export default function Price({
	children,
	currency = 'RUB',
	className,
}: PropsWithChildren & { currency?: SupportedCurrencies; className?: string }) {
	return (
		<div className={cn('price inline-flex items-center', className)}>
			{children}
			<span className="ml-1">
				{getCurrencySymbolFromCurrencyName(currency)}
			</span>
		</div>
	);
}

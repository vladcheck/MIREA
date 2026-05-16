import type { Product } from '@root-shared/types/Product';
import { observer } from 'mobx-react-lite';
import { useContext, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router';
import ApiContext from '@/features/api/ApiContext';
import useCart from '@/features/cart/useCart';
import FlexContainer from '@/shared/ui/FlexContainer';
import FullProductCard from '../ui/FullProductCard';

const ProductPage = observer(function ProductPage() {
	const { id } = useParams();
	const { api } = useContext(ApiContext);
	const [product, setProduct] = useState<Product>();
	const cart = useCart();

	useEffect(() => {
		if (id) {
			api
				?.getProductById(id)
				.then((res) => setProduct(res.data))
				.catch((error) => console.error(error));
		}
	}, [api, id]);

	return product ? (
		<FullProductCard
			p={product}
			onAddToCart={() => {
				if (id) {
					cart.addToCard(id);
				}
			}}
			onRemoveFromCart={() => {
				if (id) {
					cart.removeFromCart(id);
				}
			}}
			inCart={(id && cart.getCartItems().get(id)) || 0}
		/>
	) : (
		<FlexContainer flexDir="col" justify="center" align="center">
			<h2 className="text-3xl">Мы не можем найти данный товар</h2>
			<Link to={'/shop'}>Перейти в каталог</Link>
		</FlexContainer>
	);
});

export default ProductPage;

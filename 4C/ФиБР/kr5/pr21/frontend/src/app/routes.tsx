import { Route, Routes } from 'react-router';
import Layout from '@/pages/admin/layout';
import AdminProductsPage from '@/pages/admin/products/page';
import AdminUsersPage from '@/pages/admin/users/page';
import RootLayout from '@/pages/layout.tsx';
import LoginPage from '@/pages/login/page.tsx';
import NotFoundPage from '@/pages/notFound';
import ProductPage from '@/pages/products/[:id]/page';
import CreateProductPage from '@/pages/products/create/page';
import EditProductPage from '@/pages/products/edit/[:id]/page';
import ProductsPage from '@/pages/products/page';
import ProfilePage from '@/pages/profile/page.tsx';
import RegisterPage from '@/pages/register/page.tsx';

export default function SiteRoutes() {
	return (
		<Routes>
			<Route element={<RootLayout />}>
				<Route element={<ProductsPage />} />
				<Route path="/shop" element={<ProductsPage />} />
				<Route path="/products">
					<Route path="/products/:id" element={<ProductPage />} />
					<Route path="/products/create" element={<CreateProductPage />} />
					<Route path="/products/edit/:id" element={<EditProductPage />} />
				</Route>
				<Route path="/profile" element={<ProfilePage />} />
				<Route path="/register" element={<RegisterPage />} />
				<Route path="/login" element={<LoginPage />} />
				<Route path="/admin" element={<Layout />}>
					<Route path="/admin/users" element={<AdminUsersPage />} />
					<Route path="/admin/products" element={<AdminProductsPage />} />
				</Route>
				<Route path="*" element={<NotFoundPage />} />
			</Route>
		</Routes>
	);
}

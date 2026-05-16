import type { Product } from "@root-shared/types/Product";
import type { AxiosResponse } from "axios";
import { useEffect, useState } from "react";
import useApi from "@/features/api/hooks/useApi";
import useNotify from "@/features/notifications/useNotify";
import CatalogueProductCard from "@/pages/products/ui/CatalogueProductCard";

export default function AdminProductsPage() {
  const api = useApi();
  const notifier = useNotify();
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    api
      .getProducts()
      .then((response: AxiosResponse<{ items: Product[] }>) =>
        setProducts(response.data.items),
      )
      .catch((error: string) => notifier.notifyError(error));
  }, []);

  return (
    <main className="p-8 space-y-8 animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-color tracking-tight">
            Все товары
          </h1>
          <p className="text-text-muted mt-1">
            Общий список всех товаров в системе для административного контроля
          </p>
        </div>
        <div className="glass-panel px-6 py-3 border border-amber-500/20 bg-amber-500/5">
          <span className="text-text-muted text-sm uppercase tracking-wider font-bold">
            Всего товаров
          </span>
          <div className="text-3xl font-black text-amber-500 leading-none mt-1">
            {products.length}
          </div>
        </div>
      </header>

      {products.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((p: Product) => (
            <CatalogueProductCard key={p.id} {...p} />
          ))}
        </div>
      ) : (
        <div className="glass-panel p-20 text-center text-text-muted italic border-dashed border-2">
          Товары не найдены. Попробуйте позже.
        </div>
      )}
    </main>
  );
}

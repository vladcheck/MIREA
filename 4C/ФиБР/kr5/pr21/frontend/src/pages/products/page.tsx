import type { Product } from "@root-shared/types/Product";
import { useEffect, useState } from "react";
import useApi from "@/features/api/hooks/useApi";
import useDebouncer from "@/shared/hooks/useDebouncer";
import FlexContainer from "@/shared/ui/FlexContainer";
import { FILTER_CONFIG } from "./const";
import type { Filters } from "./types";
import CatalogueProductCard from "./ui/CatalogueProductCard";
import Sidebar from "./ui/Sidebar";

export default function ProductsPage() {
  const api = useApi();
  const [products, setProducts] = useState<Product[]>([]);
  const [filters, setFilters] = useState<Filters>({
    price: {
      min: FILTER_CONFIG.price.min,
      max: FILTER_CONFIG.price.max,
    },
  });
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);

  useDebouncer(
    () => {
      setFilteredProducts(
        products
          .filter((p) => p.price >= filters.price.min)
          .filter((p) => p.price <= filters.price.max),
      );
    },
    1000,
    [products, filters, filters.price.min, filters.price.max],
  );

  useEffect(() => {
    api
      ?.getProducts()
      .then((res) => {
        setProducts(res.data.items);
        setFilteredProducts(res.data.items);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [api]);

  return (
    <div className="w-full max-w-350 px-6 py-8 animate-fade-in">
      {/* Hero Section */}
      <div className="mb-12 text-center max-w-2xl mx-auto animate-slide-up">
        <h2 className="text-4xl font-black mb-4 tracking-tight">Наш Каталог</h2>
        <p className="text-text-muted text-lg">
          Откройте для себя лучшие товары по выгодным ценам. Качество и стиль в
          каждой детали.
        </p>
      </div>

      <FlexContainer className="gap-8 items-start">
        <div className="sticky top-24 shrink-0 transition-all">
          <Sidebar filters={filters} setFilters={setFilters} />
        </div>

        <div className="flex-1 min-w-0">
          {filteredProducts.length ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredProducts.map((p) => (
                <CatalogueProductCard key={p.id} {...p} />
              ))}
            </div>
          ) : (
            <FlexContainer
              justify="center"
              align="center"
              className="py-20 glass-panel animate-slide-up"
            >
              <div className="text-center">
                <div className="text-4xl mb-4">🔍</div>
                <h2 className="text-2xl font-bold mb-2">Товары не найдены</h2>
                <p className="text-text-muted">
                  Попробуйте изменить параметры фильтрации
                </p>
              </div>
            </FlexContainer>
          )}
        </div>
      </FlexContainer>
    </div>
  );
}

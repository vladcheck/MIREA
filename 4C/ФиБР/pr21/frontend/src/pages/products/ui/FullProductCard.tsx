import type { Product } from "@root-shared/types/Product";
import { MessageSquare, Truck } from "lucide-react";
import { observer } from "mobx-react-lite";
import { useState } from "react";
import useApi from "@/features/api/hooks/useApi";
import { authStore } from "@/features/auth/AuthStore";
import useNotify from "@/features/notifications/useNotify";
import { useHardNavigate } from "@/shared/hooks/useHardNavigate";
import Button from "@/shared/ui/Button";
import FlexContainer from "@/shared/ui/FlexContainer";
import Price from "@/shared/ui/Price";

const FullProductCard = observer(
  ({
    p,
    inCart = 0,
    onAddToCart,
    onRemoveFromCart,
  }: {
    p: Product;
    inCart?: number;
    onAddToCart: () => void;
    onRemoveFromCart: (id: string) => void;
  }) => {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const api = useApi();
    const notifier = useNotify();
    const hardNavigate = useHardNavigate();

    const isOwner = authStore.id === p.author_id;
    const isAdmin = authStore.isAdmin;
    const canEdit = isOwner || isAdmin;

    const images = p?.images?.length ? p.images : ["/images/placeholder.webp"];

    const nextImage = () =>
      setCurrentImageIndex((prev) => (prev + 1) % images.length);
    const prevImage = () =>
      setCurrentImageIndex(
        (prev) => (prev - 1 + images.length) % images.length,
      );

    const handleDelete = async () => {
      if (window.confirm("Вы уверены, что хотите удалить этот товар?")) {
        try {
          await api.deleteProductById(p.id);
          notifier.notifySuccess("Товар успешно удален");
          hardNavigate("/shop");
        } catch (error) {
          notifier.notifyError(error as string);
        }
      }
    };

    return (
      <FlexContainer
        flexDir="col"
        className="w-full max-w-300 mx-auto px-6 py-8 animate-fade-in"
      >
        {/* Top Navigation / Breadcrumbs could go here */}

        <div className="glass-panel overflow-hidden border-none shadow-premium relative group/main flex flex-col lg:flex-row">
          {/* Image Section (Left) */}
          <div className="w-full lg:w-[55%] relative group/carousel aspect-4/5 lg:aspect-auto">
            <div className="w-full h-full overflow-hidden bg-slate-50 dark:bg-slate-900/50">
              <img
                src={
                  images[currentImageIndex].startsWith("http")
                    ? images[currentImageIndex]
                    : `http://localhost:3005/images/products${images[currentImageIndex].replace("/images/products", "")}`
                }
                alt={p.title}
                className="w-full h-full object-cover transition-all duration-1000 group-hover/main:scale-105"
              />
            </div>

            {images.length > 1 && (
              <>
                <div className="absolute inset-0 flex items-center justify-between px-6 opacity-0 group-hover/carousel:opacity-100 transition-opacity duration-500 pointer-events-none">
                  <Button
                    onClick={prevImage}
                    variant="glass"
                    size="icon"
                    rounded="full"
                    pointerEvents="auto"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="m15 18-6-6 6-6" />
                    </svg>
                  </Button>
                  <Button
                    onClick={nextImage}
                    variant="glass"
                    size="icon"
                    rounded="full"
                    pointerEvents="auto"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="m9 18 6-6 6-6" />
                    </svg>
                  </Button>
                </div>
                <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2.5 bg-black/10 dark:bg-white/10 px-4 py-2 rounded-full backdrop-blur-xl border border-white/10">
                  {images.map((_, i: number) => (
                    <button
                      key={`dot-${i}`}
                      onClick={() => setCurrentImageIndex(i)}
                      className={`w-2 h-2 rounded-full transition-all duration-300 ${i === currentImageIndex ? "bg-white w-6" : "bg-white/40 hover:bg-white/60"}`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Content Section (Right) */}
          <div className="flex-1 p-8 lg:p-12 flex flex-col justify-between bg-white dark:bg-dark-surface/30 animate-slide-up">
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <span className="text-xs font-black uppercase tracking-widest text-primary bg-primary/10 px-3.5 py-1.5 rounded-full border border-primary/10">
                  {p.category}
                </span>
                <div className="h-px flex-1 bg-linear-to-r from-border-color to-transparent" />
              </div>

              <h1 className="text-4xl font-black tracking-tight leading-[1.1] text-text-color">
                {p.title}
              </h1>

              <div className="flex items-center gap-4">
                <Price className="text-4xl font-black text-primary">
                  {p.price}
                </Price>
                <div className="text-sm text-text-muted font-medium bg-green-500/10 text-green-600 px-3 py-1 rounded-lg">
                  В наличии
                </div>
              </div>

              <div className="prose dark:prose-invert max-w-none">
                <p className="text-lg text-text-muted leading-relaxed">
                  {p.description}
                </p>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-border-color/50">
              <FlexContainer className="gap-4 flex-col sm:flex-row">
                <FlexContainer
                  align="center"
                  className="bg-slate-100 h-12 dark:bg-slate-800 p-1.5 rounded-2xl gap-6 border border-border-color/50 shadow-inner"
                >
                  <Button
                    onClick={() => onRemoveFromCart(p.id)}
                    variant="secondary-danger"
                    size="icon"
                    rounded="xl"
                  >
                    −
                  </Button>
                  <span className="text-2xl font-black min-w-6 text-center text-primary">
                    {inCart}
                  </span>
                  <Button
                    onClick={onAddToCart}
                    variant="secondary-success"
                    size="icon"
                    rounded="xl"
                  >
                    +
                  </Button>
                </FlexContainer>
                <Button
                  onClick={onAddToCart}
                  variant="primary"
                  className="h-12"
                  rounded="2xl"
                  fullWidth
                >
                  Добавить в корзину
                </Button>
              </FlexContainer>

              <div className="mt-6 flex items-center justify-center gap-2 text-xs text-text-muted font-medium">
                <Truck size={14} className="text-primary" />
                <span>Бесплатная доставка при заказе от 5000₽</span>
              </div>
            </div>
          </div>
        </div>

        {/* Reviews / Additional Info Panel */}
        <div
          className="mt-8 glass-panel p-8 animate-slide-up"
          style={{ animationDelay: "0.2s" }}
        >
          <FlexContainer justify="between" align="center" className="mb-8 p-0">
            <h2 className="text-2xl font-black flex items-center gap-3">
              Отзывы покупателей
              <span className="text-xs bg-slate-100 dark:bg-slate-800 text-text-muted px-3 py-1 rounded-full font-bold">
                0
              </span>
            </h2>
            <Button variant="ghost-primary">Написать отзыв</Button>
          </FlexContainer>

          <div className="py-16 text-center bg-slate-50/50 dark:bg-slate-900/20 rounded-3xl border-2 border-dashed border-border-color/50">
            <MessageSquare
              size={48}
              className="mx-auto mb-4 opacity-20 text-text-muted"
            />
            <p className="text-lg text-text-muted italic">
              Пока нет отзывов для этого товара. Будьте первым!
            </p>
          </div>
        </div>
      </FlexContainer>
    );
  },
);

export default FullProductCard;

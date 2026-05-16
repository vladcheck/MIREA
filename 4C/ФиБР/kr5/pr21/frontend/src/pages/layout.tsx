import { ShoppingCart } from "lucide-react";
import { observer } from "mobx-react-lite";
import { useEffect, useState } from "react";
import { Link, Outlet } from "react-router";
import { ToastContainer } from "react-toastify";
import useUserInfo from "@/features/api/hooks/useUserInfo";
import useApi from "@/features/api/hooks/useApi";
import useCart from "@/features/cart/useCart";
import useNotify from "@/features/notifications/useNotify";
import logo from "@/shared/svg/logo.svg";
import Button from "@/shared/ui/Button";
import FlexContainer from "@/shared/ui/FlexContainer";
import Footer from "@/shared/ui/Footer";
import Header from "@/shared/ui/Header";
import Input from "@/shared/ui/Input";
import Main from "@/shared/ui/Main";
import ProfileImage from "@/shared/ui/ProfileImage";

const RootLayout = observer(function RootLayout() {
  const api = useApi();
  const userInfo = useUserInfo();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const cart = useCart();
  const notify = useNotify();

  useEffect(() => {
    api
      .isLoggedIn()
      .then((v) => setIsLoggedIn(v))
      .catch(() => setIsLoggedIn(false));
  }, [api]);

  const cartTotalItems = Array.from(cart.getCartItems().values()).reduce(
    (a, b) => a + b,
    0,
  );

  const startPayment = () => {
    if (cartTotalItems === 0) {
      notify.notifyWarning("Ваша корзина пуста!");
      return;
    }
    notify.notifySuccess("Оплата прошла успешно! Ваш заказ оформлен.", 3000);
    cart.clearCart();
  };

  return (
    <div id="root" className="min-h-screen flex flex-col animate-fade-in">
      <Header className="glass-nav">
        <Logo />

        <div className="flex-1 max-w-xl mx-8 relative group">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted group-focus-within:text-primary transition-colors">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </div>
          <Input
            className="premium-input py-2.5 pl-11 text-sm"
            type="search"
            name="productSearch"
            id="product-search"
            placeholder="Поиск товаров..."
            required={false}
          />
        </div>

        <FlexContainer className="gap-6" align="center">
          <FlexContainer align="center" className="gap-4">
            <Button
              variant="secondary"
              size="icon"
              rounded="xl"
              onClick={startPayment}
              className="relative"
            >
              <ShoppingCart size={20} className="text-primary" />
              {cartTotalItems > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-primary text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white dark:border-dark-surface animate-bounce">
                  {cartTotalItems}
                </span>
              )}
            </Button>
          </FlexContainer>

          <div className="h-6 w-px bg-border-color" />

          {!isLoggedIn ? (
            <FlexContainer className="gap-4" align="center">
              <Link
                to={"/register"}
                className="text-sm font-medium text-text-muted hover:text-primary transition-colors"
              >
                Регистрация
              </Link>
              <Link to={"/login"}>
                <Button className="bg-primary text-white px-6 py-2 rounded-xl text-sm hover:shadow-primary/20">
                  Войти
                </Button>
              </Link>
            </FlexContainer>
          ) : (
            <FlexContainer className="gap-5" align="center">
              {userInfo?.roles.includes("admin") && (
                <Link
                  to={"/admin/users"}
                  className="text-sm font-bold text-red-500 hover:text-red-600 transition-colors bg-red-500/5 px-3 py-1 rounded-lg border border-red-500/10"
                >
                  Админ
                </Link>
              )}
              {userInfo?.roles.includes("seller") && (
                <Link
                  to={"/products/create"}
                  className="text-sm font-bold text-amber-600 hover:text-amber-700 transition-colors bg-amber-500/5 px-3 py-1 rounded-lg border border-amber-500/10"
                >
                  Создать
                </Link>
              )}
              <div className="hover:scale-105 transition-transform">
                <ProfileImage to={"/profile"} />
              </div>
            </FlexContainer>
          )}
        </FlexContainer>
      </Header>

      <Main className="flex flex-col items-center">
        <Outlet />
      </Main>
      <Footer />
      <ToastContainer theme="auto" />
    </div>
  );
});

export default RootLayout;

function Logo() {
  return (
    <Link to={"/shop"} className="hover:opacity-80 transition-opacity">
      <FlexContainer className="gap-3" align="center">
        {logo ? (
          <img
            src={logo}
            alt="🪼"
            width={28}
            height={28}
            className="rounded-lg shadow-sm hue-rotate-200"
          />
        ) : (
          <span className="text-4xl">🪼</span>
        )}
        <h1 className="text-xl font-black bg-linear-to-r from-primary to-primary-hover bg-clip-text text-transparent">
          E-commerce
        </h1>
      </FlexContainer>
    </Link>
  );
}

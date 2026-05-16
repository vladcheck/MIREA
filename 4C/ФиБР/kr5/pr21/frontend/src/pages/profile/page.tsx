import type { Product } from "@root-shared/types/Product";
import { useEffect, useState } from "react";
import { Link } from "react-router";
import useUserInfo from "@/features/api/hooks/useUserInfo";
import useApi from "@/features/api/hooks/useApi";
import useNotify from "@/features/notifications/useNotify";
import { useHardNavigate } from "@/shared/hooks/useHardNavigate";
import FlexContainer from "@/shared/ui/FlexContainer";
import CatalogueProductCard from "../products/ui/CatalogueProductCard";
import AccountActions from "./ui/AccountActions";
import UserInfoCard from "./ui/UserInfoCard";

export default function ProfilePage() {
  const hardNavigate = useHardNavigate();
  const api = useApi();
  const notifier = useNotify();
  const userInfo = useUserInfo();
  const [userProducts, setUserProducts] = useState<undefined | Product[]>([]);

  useEffect(() => {
    api.isLoggedIn().then((isLoggedIn: boolean) => {
      if (!isLoggedIn) {
        hardNavigate("/login");
      }
    });
  }, []);

  useEffect(() => {
    if (!userInfo?.id) return;
    api
      .getProducts(userInfo?.id)
      .then((res) => setUserProducts(res.data.items))
      .catch((error) => notifier.notifyError(error));
  }, [userInfo?.id]);

  const onLogOut = () => {
    if (!userInfo) return;
    const confirm = window.confirm("Вы точно хотите выйти из аккаунта?");
    if (!confirm) return;
    api
      .logOut()
      .then(() => {
        hardNavigate("/shop");
      })
      .catch((error: string) => {
        notifier.notifyError(
          "Не удалось выйти из аккаунта, попробуйте позже.",
          3000,
        );
        console.error(error);
      });
  };

  const onDeleteAccount = () => {
    if (!userInfo) return;
    const confirm = window.confirm(
      "Вы точно хотите удалить свой аккаунт? Это действие нельзя отменить!",
    );
    if (!confirm) return;
    api
      .deleteSelf()
      .then(() => {
        notifier.notifySuccess("Аккаунт удален.");
        setTimeout(() => {
          hardNavigate("/shop");
        }, 1000);
      })
      .catch((error: string) => {
        notifier.notifyError(
          `Не удалось удалить аккаунт, попробуйте позже. ${error}`,
          3000,
        );
        console.error(error);
      });
  };

  return (
    userInfo && (
      <FlexContainer flexDir="col" className="gap-10 max-w-[90dvh]">
        <h1 className="text-3xl">Ваш профиль</h1>
        <FlexContainer flexDir="col" className="gap-6">
          <UserInfoCard label="Имя" value={userInfo.firstName} />
          <UserInfoCard label="Фамилия" value={userInfo.lastName} />
          <UserInfoCard label="Почта" value={userInfo.email} />
          <UserInfoCard label="Роли" value={userInfo.roles.join(", ")} />
        </FlexContainer>
        {userInfo.roles.includes("seller") && (
          <div>
            <h2 className="text-2xl font-semibold">Товары</h2>
            {userProducts?.length ? (
              <div className="grid grid-cols-4 gap-2">
                {userProducts?.map((p) => (
                  <CatalogueProductCard key={p.id} {...p} />
                ))}
              </div>
            ) : (
              <FlexContainer flexDir="col" className="gap-1">
                <span>У вас нет опубликованных товаров</span>
                <Link
                  to={"/products/create"}
                  className="text-blue-700 underline"
                >
                  Опубликуйте свой первый товар
                </Link>
              </FlexContainer>
            )}
          </div>
        )}
        <AccountActions onDeleteAccount={onDeleteAccount} onLogOut={onLogOut} />
      </FlexContainer>
    )
  );
}

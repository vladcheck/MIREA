import { Link, Outlet } from "react-router";
import useUserInfo from "@/features/api/hooks/useUserInfo";
import FlexContainer from "@/shared/ui/FlexContainer";
import ProtectedRouteError from "@/widgets/ProtectedRouteError";
import { ReactNode } from "react";

export default function Layout() {
  const userInfo = useUserInfo();

  if (userInfo && !userInfo?.roles.includes("admin")) {
    return <ProtectedRouteError reason="Вы не являетесь администратором." />;
  }

  return (
    userInfo && (
      <FlexContainer
        flexDir="col"
        justify="center"
        align="center"
        className="gap-6"
      >
        <FlexContainer
          justify="center"
          align="center"
          className="tabs p-2 gap-6 text-2xl max-w-max"
        >
          <Tab to={"/admin/users"}>Пользователи</Tab>
          <Tab to={"/admin/products"}>Товары</Tab>
        </FlexContainer>
        <Outlet />
      </FlexContainer>
    )
  );
}

function Tab({ children, to }: { children: ReactNode; to: string }) {
  return (
    <Link
      to={to}
      className="transition-all border-b border-b-primary hover:border-b-primary-hover hover:text-primary-hover"
    >
      {children}
    </Link>
  );
}

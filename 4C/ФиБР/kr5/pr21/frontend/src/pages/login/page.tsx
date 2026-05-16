import type { UserLoginResponse } from "@root-shared/types/User";
import type { AxiosResponse } from "axios";
import { runInAction } from "mobx";
import { observer, useLocalObservable } from "mobx-react-lite";
import { useRef } from "react";
import { Link } from "react-router";
import useApi from "@/features/api/hooks/useApi";
import { authStore } from "@/features/auth/AuthStore";
import useNotify from "@/features/notifications/useNotify";
import { useHardNavigate } from "@/shared/hooks/useHardNavigate";
import FlexContainer from "@/shared/ui/FlexContainer";
import Input from "@/shared/ui/Input";
import SubmitButton from "@/shared/ui/SubmitButton";

const LoginPage = observer(function LoginPage() {
  const hardNavigate = useHardNavigate();
  const notifier = useNotify();
  const formRef = useRef<HTMLFormElement>(null);
  const api = useApi();
  const formState = useLocalObservable(() => ({
    email: "",
    password: "",
  }));

  const onSubmit = () => {
    if (
      formRef.current?.checkValidity() &&
      formState.email &&
      formState.password
    ) {
      api
        .login(formState)
        .then((response: AxiosResponse<UserLoginResponse>) => {
          const { accessToken, refreshToken, id } = response.data;
          // Note: roles are not returned by login currently, we'd need to fetch /me or include them in JWT
          authStore.setAuth(accessToken, refreshToken, id, []);
          notifier.notifySuccess(`Вы вошли в аккаунт ${formState.email}`);
          setTimeout(() => {
            hardNavigate("/shop");
          }, 2000);
        })
        .catch((error: string) => {
          notifier.notifyError(error);
          console.error(error);
        });
    }
  };

  return (
    <FlexContainer
      flexDir="col"
      justify="center"
      align="center"
      className="min-h-[80vh] w-full px-6 animate-fade-in"
    >
      <div className="glass-panel w-full max-w-md p-10 animate-slide-up shadow-premium">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-black mb-3 tracking-tight">
            С возвращением
          </h1>
          <p className="text-text-muted">
            Введите свои данные для входа в аккаунт
          </p>
        </div>

        <form
          ref={formRef}
          className="flex flex-col gap-6"
          id="login-form"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <div className="space-y-2">
            <label
              htmlFor="email"
              className="text-sm font-bold ml-1 text-text-muted"
            >
              Почта
            </label>
            <Input
              type="email"
              value={formState.email}
              onChange={(e) => {
                runInAction(() => {
                  formState.email = e.target.value;
                });
              }}
              id="email"
              placeholder="example@mail.com"
              className="premium-input py-3.5"
              required
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center px-1">
              <label
                htmlFor="password"
                className="text-sm font-bold text-text-muted"
              >
                Пароль
              </label>
              <Link
                to="/forgot-password"
                className="text-xs font-bold text-primary hover:underline"
              >
                Забыли?
              </Link>
            </div>
            <Input
              type="password"
              value={formState.password}
              onChange={(e) => {
                runInAction(() => {
                  formState.password = e.target.value;
                });
              }}
              id="password"
              placeholder="••••••••"
              className="premium-input py-3.5"
              required
            />
          </div>

          <SubmitButton
            formId="login-form"
            onClick={onSubmit}
            variant="primary"
            size="xl"
            rounded="2xl"
            fullWidth
          >
            Войти
          </SubmitButton>
        </form>

        <div className="mt-10 pt-6 border-t border-border-color/50 text-center">
          <p className="text-sm text-text-muted font-medium">
            Нет аккаунта?{" "}
            <Link
              to="/register"
              className="text-primary font-black hover:underline underline-offset-4"
            >
              Зарегистрироваться
            </Link>
          </p>
        </div>
      </div>
    </FlexContainer>
  );
});

export default LoginPage;

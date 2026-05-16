import { fakerEN_US } from "@faker-js/faker";
import type { UserLoginResponse, UserRole } from "@root-shared/types/User";
import type { AxiosResponse } from "axios";
import { Wand2 } from "lucide-react";
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
import TextInput from "@/shared/ui/TextInput";
import { Errors, FormState } from "./types";

const RegisterPage = observer(function RegisterPage() {
  const notifier = useNotify();
  const api = useApi();
  const hardNavigate = useHardNavigate();
  const formRef = useRef<HTMLFormElement>(null);

  const formState = useLocalObservable(
    (): FormState => ({
      firstName: "",
      lastName: "",
      password: "",
      submitPassword: "",
      email: "",
      roles: ["user"],
      errors: {},
    }),
  );

  function fillWithRandomData() {
    const password = "Password123!";
    runInAction(() => {
      formState.firstName = fakerEN_US.person.firstName();
      formState.lastName = fakerEN_US.person.lastName();
      formState.email = fakerEN_US.internet.email();
      formState.password = password;
      formState.submitPassword = password;
      formState.roles = ["user"];
      formState.errors = {};
    });
  }

  const onSubmit = async () => {
    if (formStateIsValid(formState)) {
      api
        .createUser({
          firstName: formState.firstName,
          lastName: formState.lastName,
          email: formState.email,
          password: formState.password,
          roles: formState.roles,
        })
        .then((response: AxiosResponse<UserLoginResponse>) => {
          const { accessToken, refreshToken, id } = response.data;
          authStore.setAuth(accessToken, refreshToken, id, formState.roles);
          notifier.notifySuccess("Вы успешно зарегистрировались", 3000);
          setTimeout(() => {
            hardNavigate("/shop");
          }, 1000);
        })
        .catch((error: Error) => {
          notifier.notifyError(error.message);
        });
    }
  };

  return (
    <FlexContainer
      flexDir="col"
      justify="center"
      align="center"
      className="min-h-[90vh] w-full px-6 py-12 animate-fade-in"
    >
      <div className="glass-panel w-full max-w-2xl p-10 animate-slide-up shadow-premium">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-black mb-3 tracking-tight">
            Создать аккаунт
          </h1>
          <p className="text-text-muted">
            Присоединяйтесь к нашему сообществу сегодня
          </p>
        </div>

        <form
          ref={formRef}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
          id="register-form"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <div className="md:col-span-2 flex justify-end">
            <button
              type="button"
              onClick={fillWithRandomData}
              className="text-xs font-bold text-primary/60 hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <Wand2 size={14} />
              Заполнить тестовыми данными
            </button>
          </div>

          <div className="space-y-2">
            <label
              htmlFor="firstName"
              className="text-sm font-bold ml-1 text-text-muted"
            >
              Имя ૮ ˙Ⱉ˙ ა rawr!
            </label>
            <TextInput
              value={formState.firstName}
              onChange={(e) => {
                runInAction(() => (formState.firstName = e.target.value));
              }}
              id="firstName"
              placeholder="Иван"
              className="premium-input py-3.5"
              error={formState.errors.firstName}
              required
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="lastName"
              className="text-sm font-bold ml-1 text-text-muted"
            >
              Фамилия ૮₍ ˶ᵔ ᵕ ᵔ˶ ₎ა
            </label>
            <TextInput
              value={formState.lastName}
              onChange={(e) => {
                runInAction(() => (formState.lastName = e.target.value));
              }}
              id="lastName"
              placeholder="Иванов"
              className="premium-input py-3.5"
              error={formState.errors.lastName}
              required
            />
          </div>

          <div className="md:col-span-2 space-y-2">
            <label
              htmlFor="email"
              className="text-sm font-bold ml-1 text-text-muted"
            >
              Электронная почта ㅤ/ᐠ - ˕ -マ
            </label>
            <Input
              type="email"
              value={formState.email}
              onChange={(e) => {
                runInAction(() => (formState.email = e.target.value));
              }}
              id="email"
              placeholder="ivan@example.com"
              className="premium-input py-3.5"
              error={formState.errors.email}
              required
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="text-sm font-bold ml-1 text-text-muted"
            >
              Пароль ʕಠᴥಠʔ
            </label>
            <Input
              type="password"
              value={formState.password}
              onChange={(e) => {
                runInAction(() => (formState.password = e.target.value));
              }}
              id="password"
              placeholder="••••••••"
              className="premium-input py-3.5"
              error={formState.errors.password}
              required
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="submitPassword"
              className="text-sm font-bold ml-1 text-text-muted"
            >
              {"Подтверждение <・ )))><<"}
            </label>
            <Input
              type="password"
              value={formState.submitPassword}
              onChange={(e) => {
                runInAction(() => (formState.submitPassword = e.target.value));
              }}
              id="submitPassword"
              placeholder="••••••••"
              className="premium-input py-3.5"
              error={formState.errors.submitPassword}
              required
            />
          </div>
          <div className="md:col-span-2 space-y-3">
            <label className="text-sm font-bold ml-1 text-text-muted">
              Дополнительные роли{" "}
              <span className="font-normal opacity-60">(необязательно)</span>
            </label>
            <div className="flex flex-wrap gap-3">
              {(["admin", "seller"] as UserRole[]).map((role) => (
                <button
                  key={role}
                  type="button"
                  onClick={() => {
                    runInAction(() => {
                      if (formState.roles.includes(role)) {
                        formState.roles = formState.roles.filter(
                          (r) => r !== role,
                        );
                      } else {
                        formState.roles.push(role);
                      }
                    });
                  }}
                  className={`px-4 py-2 rounded-xl text-sm font-bold border transition-all duration-200 ${
                    formState.roles.includes(role)
                      ? "bg-primary text-white border-primary"
                      : "border-border-color text-text-muted hover:border-primary hover:text-primary"
                  }`}
                >
                  {role === "admin" ? "Администратор" : "Продавец"}
                </button>
              ))}
            </div>
          </div>
        </form>

        <div className="mt-10 flex flex-col gap-6">
          <SubmitButton
            formId="register-form"
            onClick={onSubmit}
            variant="primary"
            size="xl"
            rounded="2xl"
            fullWidth
          >
            Зарегистрироваться
          </SubmitButton>

          <div className="pt-6 border-t border-border-color/50 text-center space-y-2">
            <p className="text-sm text-text-muted font-medium">
              Уже есть аккаунт?{" "}
              <Link
                to="/login"
                className="text-primary font-black hover:underline underline-offset-4"
              >
                Войти
              </Link>
            </p>
            <Link
              to="/forgot-password"
              className="block text-xs font-bold text-text-muted hover:text-primary transition-colors"
            >
              Забыли пароль?
            </Link>
          </div>
        </div>
      </div>
    </FlexContainer>
  );
});

export default RegisterPage;

function formStateIsValid(formState: FormState): boolean {
  const REGEX_PATTERNS: Record<
    keyof Pick<FormState, "email" | "password" | "firstName" | "lastName">,
    RegExp
  > = {
    firstName: /^[A-ZА-ЯЁ][a-zа-яё]{1,63}$/,
    lastName: /^[A-ZА-ЯЁ][a-zа-яё]{1,63}$/,
    email: /[a-zA-Z0-9_]{1,}@[a-z0-9]{1,}\.[a-z]{2,}/,
    password: /^[a-zA-Z0-9_{}\[\]();:!?$%.,^\\\/]{4,32}$/,
  };
  const errors: Record<string, string> = {};

  if (!formState.firstName.match(REGEX_PATTERNS.firstName)) {
    errors.firstName =
      "Имя должно начинаться с заглавной буквы и содержать только буквы";
  }

  if (!formState.lastName.match(REGEX_PATTERNS.lastName)) {
    errors.lastName =
      "Фамилия должна начинаться с заглавной буквы и содержать только буквы";
  }

  if (!formState.email.match(REGEX_PATTERNS.email)) {
    errors.email = "Некорректный формат почты";
  }

  if (!formState.password.match(REGEX_PATTERNS.password)) {
    errors.password =
      "Пароль 4-32 символов (латиница, цифры, !?:;.,$^/[](){}% )";
  }

  if (formState.password !== formState.submitPassword) {
    errors.submitPassword = "Пароли не совпадают";
  }

  runInAction(() => {
    formState.errors = errors;
  });

  return isNoErrors(errors);
}

function isNoErrors(errors: Errors): boolean {
  return Object.keys(errors).length === 0;
}

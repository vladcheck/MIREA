import { runInAction } from "mobx";
import { observer, useLocalObservable } from "mobx-react-lite";
import { useRef } from "react";
import useUserInfo from "@/features/api/hooks/useUserInfo";
import useApi from "@/features/api/hooks/useApi";
import useNotify from "@/features/notifications/useNotify";
import { useHardNavigate } from "@/shared/hooks/useHardNavigate";
import FlexContainer from "@/shared/ui/FlexContainer";
import Input from "@/shared/ui/Input";
import SubmitButton from "@/shared/ui/SubmitButton";
import Textarea from "@/shared/ui/Textarea";
import TextInput from "@/shared/ui/TextInput";
import ProtectedRouteError from "@/widgets/ProtectedRouteError";
import {
  CATEGORIES,
  FORM_ID,
  MAX_ALLOWED_PRICE,
  MAX_TITLE_LENGTH,
  MIN_ALLOWED_PRICE,
} from "./const";
import ProductCardPreview from "./ui/ProductCardPreview";

const CreateProductPage = observer(function CreateProductPage() {
  const state = useLocalObservable(() => ({
    title: "",
    description: "",
    price: MIN_ALLOWED_PRICE,
    category: "Другое",
  }));
  const api = useApi();
  const formRef = useRef<HTMLFormElement>(null);
  const notifier = useNotify();
  const hardNavigate = useHardNavigate();
  const userInfo = useUserInfo();

  const onSubmit = () => {
    if (!formRef.current?.checkValidity()) {
      formRef.current?.reportValidity();
      return;
    }
    if (!userInfo) {
      console.error("No user info found");
      return;
    }
    api
      .createProduct({ ...state, author_id: userInfo?.id })
      .then(() => {
        notifier.notifySuccess(
          "Товар опубликован, сейчас вас перекинет на страницу профиля.",
          2000,
          () => hardNavigate("/profile"),
        );
      })
      .catch((error) => {
        notifier.notifyError(error);
      });
  };

  if (userInfo && !userInfo?.roles.includes("seller")) {
    if (!userInfo?.roles.includes("admin")) {
      return <ProtectedRouteError reason="Вы не являетесь продавцом." />;
    }
  }

  return (
    <FlexContainer
      flexDir="col"
      className="w-full max-w-275 mx-auto px-6 py-10 gap-8 animate-fade-in"
    >
      <div className="text-center">
        <h1 className="text-3xl font-black tracking-tight">Новый товар</h1>
        <p className="text-text-muted mt-2">
          Заполните информацию о товаре и нажмите Опубликовать
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Form */}
        <div className="glass-panel p-8 shadow-premium order-last lg:order-first">
          <form
            ref={formRef}
            className="flex flex-col gap-5"
            id={FORM_ID}
            onSubmit={(e) => {
              e.preventDefault();
              onSubmit();
            }}
          >
            <div className="space-y-2">
              <label
                htmlFor="title"
                className="text-sm font-bold ml-1 text-text-muted"
              >
                Наименование
              </label>
              <TextInput
                value={state.title}
                onChange={(e) => {
                  runInAction(() => {
                    state.title = e.target.value;
                  });
                }}
                min={3}
                max={MAX_TITLE_LENGTH}
                id="title"
                placeholder="Например: Беспроводные наушники Sony"
                className="premium-input py-3.5"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label
                  htmlFor="price"
                  className="text-sm font-bold ml-1 text-text-muted"
                >
                  Цена (руб.)
                </label>
                <Input
                  type="number"
                  value={state.price}
                  min={MIN_ALLOWED_PRICE}
                  max={MAX_ALLOWED_PRICE}
                  onChange={(e) => {
                    runInAction(() => {
                      state.price = parseInt(e.target.value, 10);
                    });
                  }}
                  id="price"
                  className="premium-input py-3.5"
                  required
                />
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="category"
                  className="text-sm font-bold ml-1 text-text-muted"
                >
                  Категория
                </label>
                <select
                  onChange={(e) => {
                    runInAction(() => {
                      state.category = e.target.value;
                    });
                  }}
                  value={state.category}
                  name="category"
                  id="category"
                  className="premium-input py-3.5 appearance-none cursor-pointer"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <label
                htmlFor="description"
                className="text-sm font-bold ml-1 text-text-muted"
              >
                Описание
              </label>
              <Textarea
                minLength={10}
                maxLength={2000}
                value={state.description}
                onChange={(e) => {
                  runInAction(() => {
                    state.description = e.target.value;
                  });
                }}
                name="description"
                id="description"
                placeholder="Подробное описание товара, его характеристики и особенности..."
                required
                className="premium-input py-3 min-h-35 resize-none"
              />
            </div>

            <SubmitButton
              onClick={onSubmit}
              formId={FORM_ID}
              variant="primary"
              size="xl"
              rounded="2xl"
              fullWidth
            >
              Опубликовать товар
            </SubmitButton>
          </form>
        </div>

        {/* Live Preview */}
        <div className="space-y-3 lg:sticky lg:top-6">
          <p className="text-xs font-bold text-text-muted uppercase tracking-widest ml-1">
            Предпросмотр
          </p>
          <ProductCardPreview {...state} />
        </div>
      </div>
    </FlexContainer>
  );
});

export default CreateProductPage;

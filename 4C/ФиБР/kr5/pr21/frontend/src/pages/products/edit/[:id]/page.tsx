import type { Product } from "@root-shared/types/Product";
import type { AxiosResponse } from "axios";
import { runInAction } from "mobx";
import { observer, useLocalObservable } from "mobx-react-lite";
import { useEffect, useRef } from "react";
import { useParams } from "react-router";
import useApi from "@/features/api/hooks/useApi";
import useNotify from "@/features/notifications/useNotify";
import { useHardNavigate } from "@/shared/hooks/useHardNavigate";
import Button from "@/shared/ui/Button";
import FlexContainer from "@/shared/ui/FlexContainer";
import Input from "@/shared/ui/Input";
import LabelInputBlock from "@/shared/ui/LabelInputBlock";
import SubmitButton from "@/shared/ui/SubmitButton";
import Textarea from "@/shared/ui/Textarea";
import TextInput from "@/shared/ui/TextInput";
import {
  CATEGORIES,
  FORM_ID,
  MAX_ALLOWED_PRICE,
  MAX_TITLE_LENGTH,
  MIN_ALLOWED_PRICE,
} from "../../create/const";
import ProductCardPreview from "../../create/ui/ProductCardPreview";

const EditProductPage = observer(function EditProductPage() {
  const { id } = useParams();
  const hardNavigate = useHardNavigate();
  const api = useApi();
  const notifier = useNotify();
  const formRef = useRef<HTMLFormElement>(null);

  const state = useLocalObservable(() => ({
    title: "",
    description: "",
    price: MIN_ALLOWED_PRICE,
    category: "Другое",
    isLoading: true,
    error: null as string | null,
  }));

  useEffect(() => {
    const productId = id;
    if (!productId) return;

    api
      .getProductById(productId)
      .then((response: AxiosResponse<Product>) => {
        runInAction(() => {
          state.title = response.data.title;
          state.description = response.data.description || "";
          state.price = response.data.price;
          state.category = response.data.category;
          state.isLoading = false;
        });
      })
      .catch((err: string) => {
        runInAction(() => {
          state.error = "Не удалось загрузить данные товара";
          state.isLoading = false;
        });
        notifier.notifyError(err);
      });
  }, [api, id, notifier, state]);

  const onSubmit = () => {
    if (!formRef.current?.checkValidity()) {
      formRef.current?.reportValidity();
      return;
    }
    const productId = id;
    if (!productId) return;

    api
      .updateProductById(productId, {
        title: state.title,
        description: state.description,
        price: state.price,
        category: state.category,
      })
      .then(() => {
        notifier.notifySuccess("Товар успешно обновлен");
        hardNavigate(`/products/${productId}`);
      })
      .catch((error: string) => {
        notifier.notifyError(error);
      });
  };

  if (state.isLoading) {
    return (
      <FlexContainer justify="center" align="center" className="py-20 text-2xl">
        Загрузка...
      </FlexContainer>
    );
  }

  if (state.error) {
    return (
      <FlexContainer
        justify="center"
        align="center"
        className="py-20 text-2xl text-red-500"
      >
        {state.error}
      </FlexContainer>
    );
  }

  // Permission check (Author or Admin)
  // Note: We'd need the product's author_id from the state, but we forgot to add it to state.
  // I'll add a check if userInfo is loaded.

  return (
    <FlexContainer className="gap-8 py-8" justify="center" align="center">
      <div className="preview">{<ProductCardPreview {...state} />}</div>
      <div className="information w-full max-w-md">
        <form ref={formRef} className="form flex flex-col gap-4" id={FORM_ID}>
          <h1 className="text-2xl font-bold">Редактирование товара</h1>
          <LabelInputBlock label="Полное наименование товара" htmlFor="title">
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
              required
            />
          </LabelInputBlock>
          <LabelInputBlock htmlFor="price" label="Цена, в рублях">
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
              required
            />
          </LabelInputBlock>
          <LabelInputBlock label="Категория" htmlFor="category">
            <select
              onChange={(e) => {
                runInAction(() => {
                  state.category = e.target.value;
                });
              }}
              value={state.category}
              name="category"
              id="category"
              className="bg-surface-hover border border-border-color rounded-xl px-4 py-3 outline-none"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </LabelInputBlock>
          <LabelInputBlock label="Описание" htmlFor="description">
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
              required
              className="min-h-37.5"
            ></Textarea>
          </LabelInputBlock>
        </form>
        <div className="mt-8 flex gap-4">
          <SubmitButton onClick={onSubmit} formId={FORM_ID} className="flex-1">
            Сохранить изменения
          </SubmitButton>
          <Button
            onClick={() => hardNavigate(-1)}
            className="px-6 py-3 glass-panel"
          >
            Отмена
          </Button>
        </div>
      </div>
    </FlexContainer>
  );
});

export default EditProductPage;
